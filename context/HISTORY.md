# Workspace History

> Journal chronologique de toutes les sessions et décisions importantes.
> Le plus récent en haut. Mis à jour automatiquement par Claude.
>
> **Comment ça marche :** Quand je lance la commande `/update` après une session importante, ou quand je raconte un changement significatif, Claude ajoute une entrée ici automatiquement. Je n'ai pas à écrire ce fichier manuellement.

---

## 2026-06-03

### SCABOT — Initialisation du projet d'automatisation des dossiers d'achat

Création du projet SCABOT dans `livrables/ricm/scabot/`. Objectif : automatiser le flux complet de traitement des devis et factures du SCAB (soutien administratif et budgétaire du RICM).

**Architecture retenue :** Google Cloud Run (serverless) déclenché par notifications push Google Drive — le Mac n'a pas besoin d'être allumé. OCR via Google Cloud Vision API. Tout dans l'écosystème Google.

**Modules livrés :**
- OCR + séparation fiche de pré-remplissage / document commercial
- Extraction de tous les champs (montants, fournisseur, GLB, imputation, etc.)
- 5 types de garde-fous (cohérence montant/fournisseur/numéro, champs manquants, imputation invalide, CPV incertain, GLB implicite)
- Remplissage automatique des templates Word bordereau d'envoi et GLB (docxtpl)
- Moteur CPV sémantique multilingue (sentence-transformers, top 3 avec score de confiance)
- Email Gmail API avec pièces jointes auto
- Journal Excel + archivage Drive + idempotence

**Templates factices créés** (à remplacer par les vrais) : bordereau_template.docx, glb_template.docx, cpv_nomenclature.xlsx, codes_imputation.xlsx.

**Convention de nommage des sorties :** `YYYYMMDD_NP_RICM_NOM_ACHAT_BORDEREAU.docx`

**Prochaines étapes :** fournir les vrais templates Word + IDs Drive + nomenclature CPV officielle + configurer un projet GCP.

---

### Site web JPO RICM 2026 — livraison et itérations

Travail intensif sur le site vitrine des Journées Portes Ouvertes du RICM (13 et 14 juin 2026), déployé sur Netlify à l'adresse `jpo-ricm-2026.netlify.app`. Le site est un fichier HTML unique hébergé sur GitHub (`clementleperse/jpo-ricm-2026`).

**Fonctionnalités livrées :**
- Programme des deux journées avec accordéon, détection automatique du jour J et badge "En cours" inline sur l'activité active
- Plan interactif des ateliers avec carte photo zoomable, marqueurs cliquables et filtres par catégorie (tout public, démonstrations, enfants)
- Modale par atelier avec description détaillée et prix en euros
- Billetterie : 3 emplacements de banques, carnets de popotte (5/10/20/30 €), moyens de paiement
- Tarifs des activités : grille 1/2/3 € avec forfait -18 ans à 10 €
- Restauration : menu du jour avec tarifs à la carte
- Infos pratiques : horaires, adresse, accès, PMR, parking, contact
- Footer avec icônes LinkedIn et Instagram du RICM
- Countdown avant ouverture, navigation sticky avec scroll spy, bouton retour en haut

**Travail technique :**
- Refonte UX complète (zones supprimées, modales centrées, typographie, eyebrows avec lignes)
- Corrections orthographiques (combat rapproché, DDémonstration, balise HTML)
- QR code généré en Python (vert RICM) pointant vers le site Netlify
- Gestion de deux dépôts git imbriqués (jarvis-starter-kit outer + jpo-ricm-2026 inner)
- Incident git résolu : rebase incorrect ayant aplati la structure, restauré via `git reset --hard`

---

## 2026-05-29

### Installation initiale du Jarvis

- Workspace personnalisé pour Clément Hanser, basé à Poitiers
- Profil principal : Officier commissaire des armées, lieutenant au RICM, chef SCAB
- Activité : Militaire de carrière, ancien deputy CFO reconverti par choix de sens
- Objectifs court terme identifiés : maîtrise des outils IA, lancement d'un side business (200 à 500 €/mois), préparation arrivée fille en juin
- Vision long terme : millionnaire avant 35 ans, École de guerre ou contrôleur général des armées, 3e langue
- Projets actifs au démarrage : exploration side business, optimisation PEA (60k€ vers 100k€), préparation parentalité
- Domaine d'aide prioritaire : maîtrise des outils IA
- Style de communication choisi : pédagogue et explicatif, esprit critique attendu
- Note : déploiement opérationnel prévu septembre 2026 (3 mois)
