"""
Pipeline OCR : photo téléphone / scan PDF → texte brut + pages séparées.

Stratégie :
- PDF avec texte natif   → extraction directe (pdfplumber)
- PDF scanné / image     → Google Cloud Vision API (recommandé)
- Fallback local         → Tesseract
"""
import io
import os
from pathlib import Path
from typing import Tuple

import pdfplumber
from loguru import logger
from PIL import Image

from config import settings


def _vision_ocr(image_bytes: bytes) -> str:
    """OCR via Google Cloud Vision."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise RuntimeError(f"Vision API : {response.error.message}")
    return response.full_text_annotation.text


def _tesseract_ocr(image_bytes: bytes) -> str:
    """OCR local Tesseract — fallback."""
    import pytesseract
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang="fra")


def _ocr_image(image_bytes: bytes) -> str:
    if settings.ocr_engine == "vision_api":
        try:
            return _vision_ocr(image_bytes)
        except Exception as e:
            logger.warning(f"Vision API échoué ({e}), fallback Tesseract")
    return _tesseract_ocr(image_bytes)


def extraire_texte_pdf(pdf_bytes: bytes) -> list[str]:
    """
    Tente l'extraction native. Si les pages sont des images (scan),
    bascule sur OCR page par page.
    Retourne une liste de strings (une par page).
    """
    pages_texte: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            texte = page.extract_text()
            if texte and texte.strip():
                pages_texte.append(texte)
                logger.debug(f"Page {i+1} : extraction native OK")
            else:
                logger.debug(f"Page {i+1} : pas de texte natif, OCR en cours…")
                img = page.to_image(resolution=300).original
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                texte_ocr = _ocr_image(buf.getvalue())
                pages_texte.append(texte_ocr)
    return pages_texte


def extraire_texte_image(image_bytes: bytes) -> list[str]:
    """Pour les JPG/PNG uploadés directement (photo téléphone)."""
    texte = _ocr_image(image_bytes)
    return [texte]


def traiter_fichier(file_bytes: bytes, mime_type: str) -> list[str]:
    """
    Point d'entrée unique.
    Retourne une liste de strings (une par page / image).
    """
    if mime_type == "application/pdf":
        return extraire_texte_pdf(file_bytes)
    elif mime_type.startswith("image/"):
        return extraire_texte_image(file_bytes)
    else:
        raise ValueError(f"Type de fichier non supporté : {mime_type}")


def separer_fiche_document(pages: list[str]) -> Tuple[str, str]:
    """
    Convention : la fiche de pré-remplissage constitue la/les premières pages
    (détectée par la présence du marqueur SCABOT_FICHE ou des champs normés).
    Le reste = document commercial (devis/facture).

    Retourne (texte_fiche, texte_document).
    """
    MARQUEUR_FICHE = ["FICHE DE PRÉ-REMPLISSAGE", "SCABOT_FICHE", "CODE D'IMPUTATION"]
    idx_fin_fiche = 0

    for i, page in enumerate(pages):
        if any(m.lower() in page.lower() for m in MARQUEUR_FICHE):
            idx_fin_fiche = i + 1

    if idx_fin_fiche == 0:
        logger.warning("Marqueur de fiche non détecté — hypothèse : page 1 = fiche")
        idx_fin_fiche = 1

    texte_fiche = "\n\n".join(pages[:idx_fin_fiche])
    texte_document = "\n\n".join(pages[idx_fin_fiche:])

    logger.info(f"Fiche : {idx_fin_fiche} page(s) | Document : {len(pages)-idx_fin_fiche} page(s)")
    return texte_fiche, texte_document
