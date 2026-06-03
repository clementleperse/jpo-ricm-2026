# SCABOT — Automatisation des dossiers d'achat RICM/SCAB

## Vue d'ensemble

SCABOT traite automatiquement les scans de devis et factures déposés sur Google Drive et produit le bordereau d'envoi, la GLB (si requise) et l'email complet.

```
Téléphone → Drive → [Cloud Run SCABOT] → Bordereau + GLB + Email
```

## Architecture

- **Runtime** : Google Cloud Run (serverless, ton Mac n'a pas besoin d'être allumé)
- **Déclencheur** : Notifications push Google Drive (webhook)
- **OCR** : Google Cloud Vision API (+ Tesseract en fallback local)
- **CPV** : Similarité sémantique multilingue (sentence-transformers, modèle local)
- **Email** : Gmail API (OAuth2)

## Structure du projet

```
scabot/
├── main.py              # Serveur FastAPI + endpoint webhook
├── pipeline.py          # Orchestrateur du flux complet
├── ocr.py               # OCR + séparation fiche/document
├── extractor.py         # Extraction des champs
├── validator.py         # Contrôles de cohérence + garde-fous
├── filler.py            # Remplissage templates Word
├── cpv_engine.py        # Moteur CPV sémantique
├── emailer.py           # Composition + envoi email
├── archiver.py          # Archivage Drive + journal Excel
├── drive_client.py      # Client Google Drive
├── models.py            # Structures de données
├── config.py            # Configuration via .env
├── Dockerfile           # Image Cloud Run
├── requirements.txt
├── .env.example         # → copier en .env et remplir
├── templates/
│   ├── bordereau_template.docx  ← REMPLACER par le vrai template
│   └── glb_template.docx        ← REMPLACER par le vrai template
├── data/
│   ├── cpv_nomenclature.xlsx    ← REMPLACER par la nomenclature officielle
│   └── codes_imputation.xlsx    ← REMPLACER par tes codes réels
└── output/              # Fichiers générés (local)
```

## Configuration initiale

### 1. Fichier .env

```bash
cp .env.example .env
# Remplir les IDs Drive, emails, projet GCP
```

### 2. Credentials Google

Créer un projet GCP, activer les APIs suivantes :
- Google Drive API
- Gmail API
- Cloud Vision API

Générer un compte de service (`credentials/service_account.json`) et un token OAuth2 utilisateur (`credentials/token_drive.json`, `credentials/token_gmail.json`).

### 3. Remplacer les templates factices

| Fichier | Action |
|---------|--------|
| `templates/bordereau_template.docx` | Remplacer par ton vrai template Word |
| `templates/glb_template.docx` | Remplacer par ton vrai template GLB |
| `data/cpv_nomenclature.xlsx` | Remplacer par la nomenclature officielle (colonnes CODE, LIBELLE) |
| `data/codes_imputation.xlsx` | Remplacer par tes codes réels (colonne CODE) |

Les variables de template utilisent la syntaxe `{{ variable }}` (docxtpl).

### 4. Déployer sur Cloud Run

```bash
gcloud builds submit --tag gcr.io/TON_PROJET/scabot
gcloud run deploy scabot \
  --image gcr.io/TON_PROJET/scabot \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

### 5. Enregistrer les webhooks Drive

```bash
curl -X POST https://TON_SERVICE.run.app/admin/register-watch
```

À renouveler tous les 7 jours (les webhooks Drive expirent).

## Modes de fonctionnement

| MODE | Comportement |
|------|-------------|
| `revue` (défaut) | Prépare tout, n'envoie pas — valider manuellement |
| `auto` | Envoie automatiquement si tous les contrôles passent |

**Garde-fous actifs même en mode `auto` :**
- OCR illisible
- Champ obligatoire manquant
- Incohérence montant / fournisseur / numéro entre fiche et document
- Code d'imputation invalide
- Score CPV insuffisant (< 45%)
- GLB possible non cochée (alerte non bloquante)

## Convention de nommage des sorties

```
YYYYMMDD_NP_RICM_NOM_DE_LACHAT_BORDEREAU.docx
YYYYMMDD_NP_RICM_NOM_DE_LACHAT_GLB.docx
```

## Feuille de route

- [ ] Étape 1 : Fournir les vrais templates + IDs Drive + codes d'imputation
- [ ] Étape 2 : Configurer GCP (APIs + credentials)
- [ ] Étape 3 : Test local sur 1 scan réel (mode revue)
- [ ] Étape 4 : Déploiement Cloud Run
- [ ] Étape 5 : Test de bout en bout sur 2-3 cas réels
- [ ] Étape 6 : Passage en mode auto
