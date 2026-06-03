"""
Interactions avec Google Drive : download fichier, enregistrement webhook.
"""
import io
from pathlib import Path

from loguru import logger


def _build_drive_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(
        "credentials/token_drive.json",
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.file",
        ]
    )
    return build("drive", "v3", credentials=creds)


def telecharger_fichier(file_id: str) -> tuple[bytes, str]:
    """
    Télécharge le fichier Drive et retourne (contenu_bytes, mime_type).
    """
    from googleapiclient.http import MediaIoBaseDownload

    service = _build_drive_service()
    meta = service.files().get(fileId=file_id, fields="name,mimeType").execute()
    mime_type = meta.get("mimeType", "application/octet-stream")

    # Google Docs → export en PDF
    if mime_type.startswith("application/vnd.google-apps"):
        request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
        mime_type = "application/pdf"
    else:
        request = service.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    logger.info(f"Fichier téléchargé : {meta['name']} ({mime_type})")
    return buf.getvalue(), mime_type


def enregistrer_webhook(folder_id: str, webhook_url: str) -> str:
    """
    Enregistre une notification push Drive sur le dossier.
    Retourne le channel_id créé.
    """
    import uuid
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(
        "credentials/token_drive.json",
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)

    channel_id = str(uuid.uuid4())
    body = {
        "id":      channel_id,
        "type":    "web_hook",
        "address": webhook_url,
        "expiration": 604800000,  # 7 jours en ms (max Drive)
    }
    response = service.files().watch(fileId=folder_id, body=body).execute()
    logger.info(f"Webhook Drive enregistré : channel={channel_id} | expiration={response.get('expiration')}")
    return channel_id
