FROM python:3.11-slim

# Dépendances système pour Tesseract + pdf2image
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pré-télécharger le modèle sentence-transformers au build (pas au runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p output credentials

EXPOSE 8080
CMD ["python", "main.py"]
