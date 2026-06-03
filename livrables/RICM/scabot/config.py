from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Google Cloud
    google_application_credentials: str = "credentials/service_account.json"
    google_cloud_project: str = ""

    # Drive
    drive_folder_devis: str = ""
    drive_folder_factures: str = ""
    drive_folder_sortie: str = ""

    # Gmail
    gmail_sender: str = ""
    email_destinataire_defaut: str = "clement.hanser@audencia.com"

    # Mode
    mode: str = "revue"  # "auto" | "revue"

    # Webhook
    webhook_url: str = ""

    # OCR
    ocr_engine: str = "vision_api"  # "vision_api" | "tesseract"

    # Seuils
    cpv_score_min: float = 0.45
    montant_ecart_max: float = 0.01

    # Chemins internes
    templates_dir: Path = Path("templates")
    data_dir: Path = Path("data")
    output_dir: Path = Path("output")
    journal_path: Path = Path("journal.xlsx")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
