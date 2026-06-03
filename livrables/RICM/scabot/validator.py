"""
Contrôles de cohérence entre la fiche et le document commercial.
Toute anomalie → alerte. L'envoi auto est bloqué si alertes non vides.
"""
from decimal import Decimal
from typing import Optional

from loguru import logger

from config import settings
from models import AlerteAnomalie, FicheAchat


# ─── Champs obligatoires ────────────────────────────────────────────────────

CHAMPS_OBLIGATOIRES = [
    ("type_document",     "Type de document"),
    ("date_reception",    "Date de réception"),
    ("fournisseur_nom",   "Fournisseur"),
    ("objet_achat",       "Objet de l'achat"),
    ("montant_ttc",       "Montant TTC"),
    ("codes_imputation",  "Code(s) d'imputation"),
    ("service_demandeur", "Service demandeur"),
]

CHAMPS_GLB_OBLIGATOIRES = [
    ("glb_categorie",      "Catégorie GLB"),
    ("glb_quantite",       "Quantité GLB"),
    ("glb_lieu_detention", "Lieu de détention GLB"),
    ("glb_detenteur",      "Détenteur GLB"),
]


def verifier_champs_obligatoires(fiche: FicheAchat) -> list[AlerteAnomalie]:
    alertes = []
    for attr, libelle in CHAMPS_OBLIGATOIRES:
        valeur = getattr(fiche, attr)
        if not valeur:
            alertes.append(AlerteAnomalie(
                code="CHAMP_MANQUANT",
                message=f"Champ obligatoire absent : {libelle}",
                champ=attr,
            ))

    if fiche.glb_requise:
        for attr, libelle in CHAMPS_GLB_OBLIGATOIRES:
            valeur = getattr(fiche, attr)
            if not valeur:
                alertes.append(AlerteAnomalie(
                    code="CHAMP_GLB_MANQUANT",
                    message=f"GLB cochée mais champ manquant : {libelle}",
                    champ=attr,
                ))
    return alertes


# ─── Cohérence fiche ↔ document ─────────────────────────────────────────────

def _ecart_relatif(a: Decimal, b: Decimal) -> float:
    if b == 0:
        return float("inf")
    return abs(float(a - b)) / float(b)


def verifier_coherence(fiche: FicheAchat, doc_data: dict) -> list[AlerteAnomalie]:
    alertes = []

    # Montant TTC
    if fiche.montant_ttc and doc_data.get("montant_ttc"):
        ecart = _ecart_relatif(fiche.montant_ttc, doc_data["montant_ttc"])
        if ecart > settings.montant_ecart_max:
            alertes.append(AlerteAnomalie(
                code="MONTANT_INCOHERENT",
                message=f"Écart de montant TTC : fiche={fiche.montant_ttc} / document={doc_data['montant_ttc']} (écart {ecart:.1%})",
                champ="montant_ttc",
                valeur_fiche=str(fiche.montant_ttc),
                valeur_document=str(doc_data["montant_ttc"]),
            ))

    # Numéro de facture/devis
    if fiche.numero_facture_devis and doc_data.get("numero"):
        if fiche.numero_facture_devis.strip() != doc_data["numero"].strip():
            alertes.append(AlerteAnomalie(
                code="NUMERO_INCOHERENT",
                message=f"N° de document différent : fiche='{fiche.numero_facture_devis}' / document='{doc_data['numero']}'",
                champ="numero_facture_devis",
                valeur_fiche=fiche.numero_facture_devis,
                valeur_document=doc_data["numero"],
            ))

    # Fournisseur (comparaison souple)
    if fiche.fournisseur_nom and doc_data.get("fournisseur"):
        nom_fiche = fiche.fournisseur_nom.lower().strip()
        nom_doc   = doc_data["fournisseur"].lower().strip()
        if nom_fiche not in nom_doc and nom_doc not in nom_fiche:
            alertes.append(AlerteAnomalie(
                code="FOURNISSEUR_INCOHERENT",
                message=f"Fournisseur différent : fiche='{fiche.fournisseur_nom}' / document='{doc_data['fournisseur']}'",
                champ="fournisseur_nom",
                valeur_fiche=fiche.fournisseur_nom,
                valeur_document=doc_data["fournisseur"],
            ))

    return alertes


# ─── Codes d'imputation ──────────────────────────────────────────────────────

def verifier_codes_imputation(fiche: FicheAchat, codes_valides: set[str]) -> list[AlerteAnomalie]:
    alertes = []
    if not codes_valides:
        return alertes  # Pas de liste fermée configurée

    for code in fiche.codes_imputation:
        if code not in codes_valides:
            alertes.append(AlerteAnomalie(
                code="IMPUTATION_INVALIDE",
                message=f"Code d'imputation inconnu : '{code}'",
                champ="codes_imputation",
                valeur_fiche=code,
            ))
    return alertes


# ─── GLB implicite ───────────────────────────────────────────────────────────

MOTS_SENSIBLES = [
    "arme", "munition", "optique", "vision nocturne", "radio", "chiffrement",
    "cryptographique", "drone", "détecteur", "surveillance", "balistique",
]

def detecter_glb_implicite(fiche: FicheAchat) -> Optional[AlerteAnomalie]:
    """Signale si l'objet semble sensible sans case GLB cochée."""
    if fiche.glb_requise or not fiche.objet_achat:
        return None
    objet_lower = fiche.objet_achat.lower()
    for mot in MOTS_SENSIBLES:
        if mot in objet_lower:
            return AlerteAnomalie(
                code="GLB_POSSIBLE",
                message=f"L'objet '{fiche.objet_achat}' contient '{mot}' — vérifier si une GLB est requise (case non cochée).",
                champ="glb_requise",
            )
    return None


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def valider_dossier(fiche: FicheAchat, doc_data: dict, codes_valides: set[str]) -> list[AlerteAnomalie]:
    alertes = []
    alertes += verifier_champs_obligatoires(fiche)
    alertes += verifier_coherence(fiche, doc_data)
    alertes += verifier_codes_imputation(fiche, codes_valides)

    alerte_glb = detecter_glb_implicite(fiche)
    if alerte_glb:
        alertes.append(alerte_glb)

    for a in alertes:
        logger.warning(f"[{a.code}] {a.message}")

    return alertes
