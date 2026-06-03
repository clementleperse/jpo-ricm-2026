"""
Extraction des champs structurés depuis le texte OCR de la fiche normée
et du document commercial.
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from loguru import logger

from models import FicheAchat, TypeDocument


# ─── Helpers ────────────────────────────────────────────────────────────────

def _nettoyer_montant(texte: str) -> Optional[Decimal]:
    """Convertit '1 234,56 €' ou '1234.56' en Decimal."""
    if not texte:
        return None
    texte = texte.strip().replace(" ", "").replace(" ", "")
    texte = texte.replace("€", "").replace("EUR", "").strip()
    texte = texte.replace(",", ".")
    try:
        return Decimal(texte)
    except InvalidOperation:
        return None


def _extraire_entre(texte: str, cle: str, fin: Optional[str] = None) -> Optional[str]:
    """Cherche la valeur après 'cle :' dans le texte."""
    pattern = rf"{re.escape(cle)}\s*[:\-]?\s*(.+)"
    if fin:
        pattern = rf"{re.escape(cle)}\s*[:\-]?\s*(.+?)(?={re.escape(fin)}|\n)"
    m = re.search(pattern, texte, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def _parse_date(texte: str) -> Optional[date]:
    """Tente JJ/MM/AAAA, AAAA-MM-JJ, JJ-MM-AAAA."""
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(texte.strip(), fmt).date()
        except ValueError:
            continue
    return None


# ─── Extraction fiche ───────────────────────────────────────────────────────

def extraire_fiche(texte_fiche: str) -> FicheAchat:
    fiche = FicheAchat()

    # Type de document
    if re.search(r"\bfacture\b", texte_fiche, re.IGNORECASE):
        fiche.type_document = TypeDocument.FACTURE
    elif re.search(r"\bdevis\b", texte_fiche, re.IGNORECASE):
        fiche.type_document = TypeDocument.DEVIS

    # Référence interne
    fiche.reference_interne = _extraire_entre(texte_fiche, "Référence interne") or \
                               _extraire_entre(texte_fiche, "N° de dossier")

    # Date de réception
    val = _extraire_entre(texte_fiche, "Date de réception") or \
          _extraire_entre(texte_fiche, "Date réception")
    if val:
        fiche.date_reception = _parse_date(val)

    # Fournisseur
    fiche.fournisseur_nom = _extraire_entre(texte_fiche, "Fournisseur")
    fiche.fournisseur_siret = _extraire_entre(texte_fiche, "SIRET")

    # Numéro facture/devis
    fiche.numero_facture_devis = _extraire_entre(texte_fiche, "N° de facture") or \
                                  _extraire_entre(texte_fiche, "N° de devis") or \
                                  _extraire_entre(texte_fiche, "Numéro")

    # Objet de l'achat
    fiche.objet_achat = _extraire_entre(texte_fiche, "Objet de l'achat") or \
                        _extraire_entre(texte_fiche, "Objet")

    # Montants
    val_ht = _extraire_entre(texte_fiche, "Montant HT")
    val_tva = _extraire_entre(texte_fiche, "TVA") or _extraire_entre(texte_fiche, "Montant TVA")
    val_ttc = _extraire_entre(texte_fiche, "Montant TTC") or _extraire_entre(texte_fiche, "TTC")
    fiche.montant_ht  = _nettoyer_montant(val_ht)  if val_ht  else None
    fiche.montant_tva = _nettoyer_montant(val_tva) if val_tva else None
    fiche.montant_ttc = _nettoyer_montant(val_ttc) if val_ttc else None

    # Devise
    if "USD" in texte_fiche.upper():
        fiche.devise = "USD"

    # Codes d'imputation (peut y en avoir plusieurs, séparés par / ou ,)
    val_imp = _extraire_entre(texte_fiche, "Code d'imputation") or \
              _extraire_entre(texte_fiche, "Codes d'imputation") or \
              _extraire_entre(texte_fiche, "Imputation")
    if val_imp:
        fiche.codes_imputation = [c.strip() for c in re.split(r"[,;/]", val_imp) if c.strip()]

    # Service demandeur
    fiche.service_demandeur = _extraire_entre(texte_fiche, "Service demandeur") or \
                               _extraire_entre(texte_fiche, "Bénéficiaire")

    # Destinataire email
    fiche.destinataire_email = _extraire_entre(texte_fiche, "Destinataire") or \
                                _extraire_entre(texte_fiche, "Email destinataire")

    # GLB — case à cocher
    glb_val = _extraire_entre(texte_fiche, "GLB")
    # Checkbox cochée : Vision API renvoie "☑" ou "[X]" ou "☒" ou "true"
    if glb_val:
        fiche.glb_requise = bool(re.search(r"(☑|☒|\[x\]|oui|true|coché)", glb_val, re.IGNORECASE))
    # Fallback : cherche directement "☑ GLB" dans le texte
    if re.search(r"(☑|☒|\[x\])\s*GLB", texte_fiche, re.IGNORECASE):
        fiche.glb_requise = True

    if fiche.glb_requise:
        fiche.glb_categorie   = _extraire_entre(texte_fiche, "Catégorie GLB") or \
                                 _extraire_entre(texte_fiche, "Catégorie")
        fiche.glb_quantite    = int(_extraire_entre(texte_fiche, "Quantité") or 0) or None
        fiche.glb_numero_serie = _extraire_entre(texte_fiche, "N° de série") or \
                                  _extraire_entre(texte_fiche, "Numéro de série")
        fiche.glb_lieu_detention = _extraire_entre(texte_fiche, "Lieu de détention")
        fiche.glb_detenteur   = _extraire_entre(texte_fiche, "Détenteur")

    # CPV imposé
    fiche.code_cpv_impose = _extraire_entre(texte_fiche, "Code CPV imposé") or \
                             _extraire_entre(texte_fiche, "CPV imposé")

    # Observations
    fiche.observations = _extraire_entre(texte_fiche, "Observations")

    logger.info(f"Fiche extraite : {fiche.fournisseur_nom} | {fiche.objet_achat} | TTC={fiche.montant_ttc}")
    return fiche


# ─── Extraction document commercial ─────────────────────────────────────────

def extraire_document(texte_doc: str) -> dict:
    """
    Extrait les données clés du devis/facture pour le contrôle de cohérence.
    Retourne un dict simple (fournisseur, numéro, montant TTC, date).
    """
    data = {}

    # Fournisseur (généralement en haut du doc)
    m = re.search(r"(?:SARL|SAS|SA|EURL|EI|Auto-entrepreneur)\s+([\w\s]+)", texte_doc)
    if m:
        data["fournisseur"] = m.group(1).strip()

    # Numéro de devis / facture
    m = re.search(r"(?:facture|devis)\s*n[°o]?\s*[:\-]?\s*([\w\-\/]+)", texte_doc, re.IGNORECASE)
    if m:
        data["numero"] = m.group(1).strip()

    # Montant TTC
    m = re.search(r"(?:total|montant)\s+ttc\s*[:\-]?\s*([\d\s.,]+)\s*€?", texte_doc, re.IGNORECASE)
    if m:
        data["montant_ttc"] = _nettoyer_montant(m.group(1))

    # Date
    m = re.search(r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b", texte_doc)
    if m:
        data["date"] = _parse_date(m.group(1))

    return data
