# Prompt Claude Design — Site JPO RICM 2026

> Coller ce prompt dans Claude Design. Remplir les zones `[EN MAJUSCULES]` avec le contenu réel avant d'envoyer.

---

Crée un site web one-page responsive, mobile-first, pour les Journées Portes Ouvertes du RICM (Régiment d'Infanterie-Chars de Marine) les 13 et 14 juin 2026 à Poitiers.

Ce site est destiné aux visiteurs qui scannent un QR code sur place. L'objectif : qu'ils trouvent immédiatement toutes les informations pour se repérer et profiter de l'événement.

---

## DESIGN

- Style militaire moderne, professionnel mais accessible aux familles
- Palette : vert militaire (#2D4A2D), beige sable (#C8B89A), rouge (#C8102E), blanc
- Typographie : titres en bold condensé (style militaire), corps en clean sans-serif
- Beaucoup d'espace blanc, icônes simples, hiérarchie visuelle claire
- Adapté à une lecture rapide sur smartphone en plein air (bon contraste)

---

## STRUCTURE DU SITE (sections dans cet ordre)

### 1. HERO
- Nom : "Portes Ouvertes RICM"
- Sous-titre : "13 & 14 juin 2026 — Poitiers"
- Bouton CTA : "Voir le programme du jour"
- Badge/ruban : "Entrée libre"

### 2. NAVIGATION STICKY (barre fixe en haut sur mobile)
Liens vers : Programme | Plan du site | Restauration | Infos pratiques

### 3. PROGRAMME
- Sélecteur de jour : deux onglets "Samedi 13 juin" / "Dimanche 14 juin"
- Pour chaque jour, liste chronologique des animations avec :
  * Heure
  * Nom de l'animation
  * Icône ou badge de catégorie (ex : démonstration, espace enfants, exposition...)
  * Lieu sur le site

**SAMEDI 13 JUIN :**
[COLLER ICI LE PROGRAMME DU SAMEDI]

**DIMANCHE 14 JUIN :**
[COLLER ICI LE PROGRAMME DU DIMANCHE]

### 4. PLAN DU SITE
- Carte schématique simplifiée du régiment avec les zones numérotées/colorées
- Légende claire : chaque zone correspond à une animation ou espace
- Si pas d'image carte disponible, créer un plan schématique SVG avec les zones suivantes :

[COLLER ICI LA LISTE DES ZONES ET LEUR POSITION RELATIVE]

### 5. RESTAURATION
- Titre : "Se restaurer sur place"
- Cards pour chaque point de restauration :
  * Nom du stand
  * Type de cuisine / formules proposées
  * Tarifs
  * Horaires d'ouverture
  * Localisation sur le plan (numéro de zone)

[COLLER ICI LES INFOS RESTAURATION]

### 6. INFOS PRATIQUES
- Horaires d'ouverture : Samedi [H]h-[H]h / Dimanche [H]h-[H]h
- Adresse : [ADRESSE DU RICM]
- Accès : [TRANSPORTS EN COMMUN / GPS]
- Parking : [INFOS PARKING]
- Accès PMR : [OUI/NON + détails]
- Objets interdits : [LISTE SI NÉCESSAIRE]
- Contact sur place : [NUMÉRO OU POINT INFO]

### 7. FOOTER
- Logo RICM (placeholder si non fourni)
- "Régiment d'Infanterie-Chars de Marine — Poitiers"
- Lien : Armée de Terre

---

## FONCTIONNALITÉS

- Le sélecteur de jour (samedi/dimanche) doit détecter automatiquement la date du jour et afficher le bon onglet par défaut les 13 et 14 juin
- Smooth scroll entre les sections
- Toutes les sections doivent être lisibles sans zoom sur un écran de 375px de large minimum
- Pas de connexion internet requise pour naviguer (pas de dépendances externes sauf Google Fonts)

---

Génère le code HTML/CSS/JS complet en un seul fichier autonome.
