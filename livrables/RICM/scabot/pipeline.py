"""
Orchestrateur principal : reçoit un file_id Drive et pilote tout le flux.
"""
from pathlib import Path

from loguru import logger

from archiver import archiver_sur_drive, deja_traite, journaliser
from config import settings
from cpv_engine import proposer_cpv, verifier_seuil_cpv
from drive_client import telecharger_fichier
from emailer import envoyer_email
from extractor import extraire_document, extraire_fiche
from filler import remplir_bordereau, remplir_glb
from models import AlerteAnomalie, DossierTraitement, StatutTraitement
from ocr import separer_fiche_document, traiter_fichier
from validator import valider_dossier


def _charger_codes_imputation() -> set[str]:
    """Charge la liste fermée des codes d'imputation depuis l'Excel."""
    import pandas as pd
    chemin = settings.data_dir / "codes_imputation.xlsx"
    if not chemin.exists():
        logger.warning("Fichier codes_imputation.xlsx absent — validation désactivée")
        return set()
    df = pd.read_excel(chemin, dtype=str)
    col = df.columns[0]
    return set(df[col].dropna().str.strip().tolist())


def traiter_document(file_id: str, file_name: str) -> DossierTraitement:
    """
    Flux complet pour un document.
    Retourne le DossierTraitement avec statut final.
    """
    dossier = DossierTraitement(drive_file_id=file_id, drive_file_name=file_name)

    # ── 0. Idempotence ──────────────────────────────────────────────────────
    if deja_traite(file_id):
        logger.info(f"Fichier déjà traité, ignoré : {file_name}")
        dossier.statut = StatutTraitement.SUSPENDU
        dossier.motif_suspension = "Déjà traité (idempotence)"
        return dossier

    try:
        # ── 1. Téléchargement + OCR ─────────────────────────────────────────
        logger.info(f"=== Traitement : {file_name} ({file_id}) ===")
        contenu, mime_type = telecharger_fichier(file_id)

        # Sauvegarde locale du scan original
        chemin_scan = settings.output_dir / file_name
        chemin_scan.parent.mkdir(parents=True, exist_ok=True)
        chemin_scan.write_bytes(contenu)

        pages = traiter_fichier(contenu, mime_type)

        if not pages or all(not p.strip() for p in pages):
            dossier.alertes.append(AlerteAnomalie(
                code="OCR_ILLISIBLE",
                message="L'OCR n'a produit aucun texte exploitable.",
            ))
            return _suspendre(dossier, chemin_scan)

        # ── 2. Séparation fiche / document ──────────────────────────────────
        texte_fiche, texte_doc = separer_fiche_document(pages)

        # ── 3. Extraction ───────────────────────────────────────────────────
        fiche = extraire_fiche(texte_fiche)
        doc_data = extraire_document(texte_doc)
        dossier.fiche = fiche

        # ── 4. Validation ───────────────────────────────────────────────────
        codes_valides = _charger_codes_imputation()
        alertes = valider_dossier(fiche, doc_data, codes_valides)
        dossier.alertes = alertes

        # ── 5. CPV ──────────────────────────────────────────────────────────
        if fiche.code_cpv_impose:
            from models import ResultatCPV
            dossier.cpv_retenu = ResultatCPV(
                code=fiche.code_cpv_impose,
                libelle="(imposé par la fiche)",
                score=1.0,
            )
            dossier.cpv_proposes = [dossier.cpv_retenu]
        else:
            contexte = f"{fiche.service_demandeur or ''} {fiche.fournisseur_nom or ''}"
            dossier.cpv_proposes = proposer_cpv(fiche.objet_achat or "", contexte=contexte)
            if dossier.cpv_proposes:
                dossier.cpv_retenu = dossier.cpv_proposes[0]
            if not verifier_seuil_cpv(dossier.cpv_proposes):
                dossier.alertes.append(AlerteAnomalie(
                    code="CPV_INCERTAIN",
                    message=f"Score CPV insuffisant ({dossier.cpv_retenu.score:.0%} < {settings.cpv_score_min:.0%}). Propositions : " +
                             ", ".join(f"{r.code} ({r.score:.0%})" for r in dossier.cpv_proposes),
                ))

        # ── 6. Remplissage Word ─────────────────────────────────────────────
        chemin_bordereau = remplir_bordereau(dossier)
        dossier.chemin_bordereau = str(chemin_bordereau)

        if fiche.glb_requise:
            chemin_glb = remplir_glb(dossier)
            dossier.chemin_glb = str(chemin_glb)

        # ── 7. Envoi conditionnel ───────────────────────────────────────────
        if settings.mode == "revue":
            logger.info("MODE REVUE — dossier préparé, envoi suspendu jusqu'à validation manuelle")
            dossier.statut = StatutTraitement.BROUILLON
            dossier.motif_suspension = "Mode revue actif"

        elif dossier.peut_envoyer_auto:
            logger.info("MODE AUTO — tous les contrôles passent, envoi en cours…")
            succes = envoyer_email(dossier, chemin_scan)
            dossier.statut = StatutTraitement.ENVOYE if succes else StatutTraitement.SUSPENDU
            if not succes:
                dossier.motif_suspension = "Échec d'envoi email"

        else:
            return _suspendre(dossier, chemin_scan)

    except Exception as e:
        logger.exception(f"Erreur inattendue lors du traitement : {e}")
        dossier.alertes.append(AlerteAnomalie(
            code="ERREUR_INTERNE",
            message=str(e),
        ))
        dossier.statut = StatutTraitement.SUSPENDU
        dossier.motif_suspension = f"Erreur interne : {e}"

    finally:
        # ── 8. Archivage + journal ──────────────────────────────────────────
        fichiers_a_archiver = [
            Path(p) for p in [
                str(chemin_scan) if 'chemin_scan' in locals() else None,
                dossier.chemin_bordereau,
                dossier.chemin_glb,
            ] if p
        ]
        archiver_sur_drive(dossier, fichiers_a_archiver)
        journaliser(dossier)

    return dossier


def _suspendre(dossier: DossierTraitement, chemin_scan: Path) -> DossierTraitement:
    dossier.statut = StatutTraitement.SUSPENDU
    if not dossier.motif_suspension:
        dossier.motif_suspension = " | ".join(a.message for a in dossier.alertes)
    logger.warning(f"Dossier SUSPENDU : {dossier.motif_suspension}")
    return dossier
