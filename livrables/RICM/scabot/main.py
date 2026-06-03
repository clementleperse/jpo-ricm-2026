"""
Point d'entrée Cloud Run — serveur FastAPI.

Expose deux endpoints :
  POST /webhook  : reçoit les notifications push Google Drive
  POST /admin/register-watch : (ré)enregistre les webhooks Drive sur les dossiers
  GET  /health   : health check
"""
import json
import os

from fastapi import FastAPI, Request, Response, HTTPException
from loguru import logger

from config import settings
from pipeline import traiter_document

app = FastAPI(title="SCABOT", version="1.0.0")

# ─── Health ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "mode": settings.mode}


# ─── Webhook Drive ───────────────────────────────────────────────────────────

@app.post("/webhook")
async def webhook_drive(request: Request):
    """
    Google Drive envoie une notification HTTP POST sur cet endpoint
    quand un nouveau fichier apparaît dans un dossier surveillé.

    Headers importants :
      X-Goog-Resource-State : "update" | "sync" | "add"
      X-Goog-Changed        : "children" si nouveau fichier dans un dossier
      X-Goog-Resource-Id    : ID Drive du dossier
    """
    headers = dict(request.headers)
    resource_state = headers.get("x-goog-resource-state", "")
    changed        = headers.get("x-goog-changed", "")
    resource_id    = headers.get("x-goog-resource-id", "")

    logger.info(f"Webhook reçu : state={resource_state} | changed={changed} | id={resource_id}")

    # Ignorer les messages de sync initiaux
    if resource_state == "sync":
        return Response(status_code=200)

    # Nouveau fichier dans un dossier surveillé
    if resource_state in ("update", "add") and "children" in changed:
        await _traiter_nouveaux_fichiers(resource_id)

    return Response(status_code=200)


async def _traiter_nouveaux_fichiers(folder_id: str):
    """Liste les fichiers récents du dossier et déclenche le pipeline."""
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    try:
        creds = Credentials.from_authorized_user_file(
            "credentials/token_drive.json",
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)

        # Récupère les fichiers ajoutés récemment (ordre chronologique desc)
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            orderBy="createdTime desc",
            pageSize=5,
            fields="files(id, name, mimeType, createdTime)",
        ).execute()

        fichiers = results.get("files", [])
        for f in fichiers:
            logger.info(f"Nouveau fichier détecté : {f['name']} ({f['id']})")
            dossier = traiter_document(f["id"], f["name"])
            logger.info(f"Résultat : {dossier.statut.value} | {dossier.motif_suspension or 'OK'}")

    except Exception as e:
        logger.exception(f"Erreur traitement webhook : {e}")


# ─── Admin : (ré)enregistrement des watches Drive ───────────────────────────

@app.post("/admin/register-watch")
def register_watch():
    """
    Enregistre (ou renouvelle) les notifications push Drive sur les deux
    dossiers source (DEVIS et FACTURES).
    À appeler au démarrage et avant expiration (~7 jours).
    """
    from drive_client import enregistrer_webhook

    webhook_url = settings.webhook_url
    if not webhook_url:
        raise HTTPException(status_code=500, detail="WEBHOOK_URL non configurée dans .env")

    resultats = {}
    for nom, folder_id in [
        ("DEVIS",     settings.drive_folder_devis),
        ("FACTURES",  settings.drive_folder_factures),
    ]:
        if folder_id:
            channel_id = enregistrer_webhook(folder_id, webhook_url + "/webhook")
            resultats[nom] = channel_id
        else:
            resultats[nom] = "ID dossier non configuré"

    return resultats


# ─── Démarrage ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
