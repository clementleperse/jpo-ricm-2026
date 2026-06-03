"""
Remplissage des templates Word (bordereau d'envoi + GLB).
Sorties .docx éditables.
"""
from datetime import date
from pathlib import Path

from docxtpl import DocxTemplate
from loguru import logger

from config import settings
from models import DossierTraitement, FicheAchat


def _ctx_commun(fiche: FicheAchat, dossier: DossierTraitement) -> dict:
    """Contexte partagé entre les deux templates."""
    return {
        "reference_interne":    fiche.reference_interne or "",
        "date_reception":       fiche.date_reception.strftime("%d/%m/%Y") if fiche.date_reception else "",
        "date_traitement":      date.today().strftime("%d/%m/%Y"),
        "type_document":        (fiche.type_document.value.capitalize()) if fiche.type_document else "",
        "fournisseur_nom":      fiche.fournisseur_nom or "",
        "fournisseur_siret":    fiche.fournisseur_siret or "",
        "numero_document":      fiche.numero_facture_devis or "",
        "objet_achat":          fiche.objet_achat or "",
        "montant_ht":           str(fiche.montant_ht or "").replace(".", ",") + " " + fiche.devise,
        "montant_tva":          str(fiche.montant_tva or "").replace(".", ",") + " " + fiche.devise,
        "montant_ttc":          str(fiche.montant_ttc or "").replace(".", ",") + " " + fiche.devise,
        "codes_imputation":     " / ".join(fiche.codes_imputation),
        "service_demandeur":    fiche.service_demandeur or "",
        "cpv_code":             dossier.cpv_retenu.code if dossier.cpv_retenu else "",
        "cpv_libelle":          dossier.cpv_retenu.libelle if dossier.cpv_retenu else "",
        "cpv_score":            f"{dossier.cpv_retenu.score:.0%}" if dossier.cpv_retenu else "",
        "cpv_proposes":         [
            {"code": r.code, "libelle": r.libelle, "score": f"{r.score:.0%}"}
            for r in dossier.cpv_proposes
        ],
        "pieces_jointes":       fiche.pieces_jointes or [],
        "observations":         fiche.observations or "",
        "nom_fichier_original": dossier.drive_file_name,
        "glb_requise":          "Oui" if fiche.glb_requise else "Non",
    }


def remplir_bordereau(dossier: DossierTraitement) -> Path:
    """Remplit le template bordereau et retourne le chemin du .docx généré."""
    fiche = dossier.fiche
    template_path = settings.templates_dir / "bordereau_template.docx"

    if not template_path.exists():
        raise FileNotFoundError(f"Template bordereau introuvable : {template_path}")

    tpl = DocxTemplate(str(template_path))
    ctx = _ctx_commun(fiche, dossier)

    tpl.render(ctx)

    output_path = settings.output_dir / f"{dossier.nom_sortie}_BORDEREAU.docx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tpl.save(str(output_path))

    logger.info(f"Bordereau généré : {output_path}")
    return output_path


def remplir_glb(dossier: DossierTraitement) -> Path:
    """Remplit le template GLB. N'appeler que si fiche.glb_requise."""
    fiche = dossier.fiche
    template_path = settings.templates_dir / "glb_template.docx"

    if not template_path.exists():
        raise FileNotFoundError(f"Template GLB introuvable : {template_path}")

    tpl = DocxTemplate(str(template_path))
    ctx = _ctx_commun(fiche, dossier)

    # Champs spécifiques GLB
    ctx.update({
        "glb_categorie":      fiche.glb_categorie or "",
        "glb_quantite":       str(fiche.glb_quantite or ""),
        "glb_numero_serie":   fiche.glb_numero_serie or "",
        "glb_lieu_detention": fiche.glb_lieu_detention or "",
        "glb_detenteur":      fiche.glb_detenteur or "",
    })

    tpl.render(ctx)

    output_path = settings.output_dir / f"{dossier.nom_sortie}_GLB.docx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tpl.save(str(output_path))

    logger.info(f"GLB générée : {output_path}")
    return output_path
