"""
Moteur CPV : propose les 3 codes les plus proches de l'objet acheté
via similarité sémantique (sentence-transformers, modèle local).
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd
import numpy as np
from loguru import logger

from config import settings
from models import ResultatCPV

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # multilingue, ~120 Mo, 100% local


@lru_cache(maxsize=1)
def _charger_modele():
    from sentence_transformers import SentenceTransformer
    logger.info(f"Chargement du modèle CPV : {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def _charger_cpv() -> pd.DataFrame:
    """Charge le fichier Excel CPV et pré-calcule les embeddings."""
    chemin = settings.data_dir / "cpv_nomenclature.xlsx"
    logger.info(f"Chargement nomenclature CPV : {chemin}")
    df = pd.read_excel(chemin, dtype=str)

    # Colonnes attendues : CODE, LIBELLE (adapter si nécessaire)
    df.columns = [c.strip().upper() for c in df.columns]
    if "CODE" not in df.columns or "LIBELLE" not in df.columns:
        raise ValueError("Le fichier CPV doit avoir des colonnes CODE et LIBELLE")

    df = df.dropna(subset=["CODE", "LIBELLE"])
    df["texte_embedding"] = df["CODE"] + " — " + df["LIBELLE"]

    modele = _charger_modele()
    logger.info(f"Calcul des embeddings CPV ({len(df)} lignes)…")
    embeddings = modele.encode(df["texte_embedding"].tolist(), batch_size=64, show_progress_bar=False)
    df["embedding"] = list(embeddings)

    logger.info("Nomenclature CPV prête")
    return df


def proposer_cpv(objet_achat: str, contexte: str = "", top_n: int = 3) -> list[ResultatCPV]:
    """
    Retourne les top_n codes CPV les plus proches.
    Contexte peut inclure des informations supplémentaires (service, catégorie).
    """
    if not objet_achat:
        return []

    modele = _charger_modele()
    df = _charger_cpv()

    # Enrichir la requête avec le contexte
    requete = objet_achat
    if contexte:
        requete = f"{objet_achat}. Contexte : {contexte}"

    embedding_requete = modele.encode(requete)

    # Cosine similarity
    embeddings_cpv = np.vstack(df["embedding"].values)
    scores = np.dot(embeddings_cpv, embedding_requete) / (
        np.linalg.norm(embeddings_cpv, axis=1) * np.linalg.norm(embedding_requete) + 1e-9
    )

    indices_top = np.argsort(scores)[::-1][:top_n]

    resultats = []
    for idx in indices_top:
        row = df.iloc[idx]
        resultats.append(ResultatCPV(
            code=row["CODE"],
            libelle=row["LIBELLE"],
            score=float(scores[idx]),
        ))
        logger.debug(f"CPV {row['CODE']} — {row['LIBELLE']} (score={scores[idx]:.3f})")

    return resultats


def verifier_seuil_cpv(resultats: list[ResultatCPV]) -> bool:
    """Retourne True si le meilleur score dépasse le seuil de confiance."""
    if not resultats:
        return False
    return resultats[0].score >= settings.cpv_score_min
