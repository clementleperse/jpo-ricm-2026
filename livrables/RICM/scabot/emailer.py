"""
Composition et envoi de l'email via Gmail API.
"""
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

from loguru import logger

from config import settings
from models import DossierTraitement


def _build_gmail_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(
        "credentials/token_gmail.json",
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    return build("gmail", "v1", credentials=creds)


def _construire_objet(dossier: DossierTraitement) -> str:
    fiche = dossier.fiche
    type_doc = fiche.type_document.value.upper() if fiche.type_document else "DOCUMENT"
    fournisseur = fiche.fournisseur_nom or "Fournisseur inconnu"
    ref = fiche.reference_interne or fiche.numero_facture_devis or ""
    montant = f"{fiche.montant_ttc} {fiche.devise}" if fiche.montant_ttc else ""
    return f"[SCABOT] {type_doc} — {fournisseur} — {montant} — Réf. {ref}".strip(" —")


def _construire_corps(dossier: DossierTraitement) -> str:
    fiche = dossier.fiche
    lignes_alertes = ""
    if dossier.alertes:
        lignes_alertes = "\n\nPOINTS D'ATTENTION :\n" + "\n".join(
            f"  • [{a.code}] {a.message}" for a in dossier.alertes
        )

    cpv_ligne = ""
    if dossier.cpv_retenu:
        cpv_ligne = f"\nCode CPV retenu : {dossier.cpv_retenu.code} — {dossier.cpv_retenu.libelle} (confiance {dossier.cpv_retenu.score:.0%})"

    return f"""Bonjour,

Veuillez trouver ci-joint le dossier d'achat suivant :

  Fournisseur    : {fiche.fournisseur_nom or '—'}
  Objet          : {fiche.objet_achat or '—'}
  N° document    : {fiche.numero_facture_devis or '—'}
  Date réception : {fiche.date_reception.strftime('%d/%m/%Y') if fiche.date_reception else '—'}
  Montant HT     : {fiche.montant_ht or '—'} {fiche.devise}
  Montant TTC    : {fiche.montant_ttc or '—'} {fiche.devise}
  Imputation(s)  : {' / '.join(fiche.codes_imputation) or '—'}
  GLB requise    : {'Oui' if fiche.glb_requise else 'Non'}
{cpv_ligne}

Pièces jointes :
  • Document original (scan)
  • Bordereau d'envoi{' • Feuille de perception (GLB)' if fiche.glb_requise else ''}
{lignes_alertes}

---
Message généré automatiquement par SCABOT — RICM / SCAB
Toute erreur peut être corrigée directement dans les documents Word joints.
"""


def _ajouter_piece_jointe(msg: MIMEMultipart, chemin: Path) -> None:
    mime_type, _ = mimetypes.guess_type(str(chemin))
    maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

    with open(chemin, "rb") as f:
        part = MIMEBase(maintype, subtype)
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=chemin.name)
        msg.attach(part)


def composer_email(dossier: DossierTraitement, chemin_scan: Path) -> dict:
    """
    Compose l'email et retourne le dict prêt pour Gmail API.
    """
    destinataire = (
        dossier.fiche.destinataire_email
        or settings.email_destinataire_defaut
    )

    msg = MIMEMultipart()
    msg["From"]    = settings.gmail_sender
    msg["To"]      = destinataire
    msg["Subject"] = _construire_objet(dossier)

    msg.attach(MIMEText(_construire_corps(dossier), "plain", "utf-8"))

    # Pièces jointes
    _ajouter_piece_jointe(msg, chemin_scan)
    if dossier.chemin_bordereau:
        _ajouter_piece_jointe(msg, Path(dossier.chemin_bordereau))
    if dossier.chemin_glb:
        _ajouter_piece_jointe(msg, Path(dossier.chemin_glb))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw, "destinataire": destinataire}


def envoyer_email(dossier: DossierTraitement, chemin_scan: Path) -> bool:
    """Envoie l'email. Retourne True si succès."""
    payload = composer_email(dossier, chemin_scan)
    try:
        service = _build_gmail_service()
        service.users().messages().send(
            userId="me",
            body={"raw": payload["raw"]}
        ).execute()
        logger.info(f"Email envoyé à {payload['destinataire']}")
        return True
    except Exception as e:
        logger.error(f"Échec envoi email : {e}")
        return False
