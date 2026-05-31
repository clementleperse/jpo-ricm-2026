# /commit

> Commande pour sauvegarder l'état actuel du workspace dans Git.

---

## Mission

Quand je lance `/commit`, exécute la séquence suivante :

### Étape 1 : Initialiser le dépôt si nécessaire

Vérifie si Git est déjà initialisé :

```bash
git status
```

Si ce n'est pas encore un dépôt Git, initialise-le :

```bash
git init
```

Puis vérifie qu'un fichier `.gitignore` existe. S'il n'existe pas, signale-le et arrête-toi : c'est un prérequis de sécurité.

### Étape 2 : Inspecter l'état actuel

Lance les deux commandes suivantes et analyse leur résultat :

```bash
git status
git diff --stat
```

Présente-moi un résumé lisible de ce qui a changé :

```
Voici ce qui va être sauvegardé :

Fichiers modifiés :
- [liste des fichiers modifiés]

Fichiers nouveaux :
- [liste des nouveaux fichiers]

Fichiers supprimés :
- [liste des fichiers supprimés]

Ces fichiers sont ignorés par .gitignore (jamais commités) :
- .env et variantes
- [autres patterns pertinents]
```

### Étape 3 : Proposer un message de commit

Génère un message de commit clair basé sur les changements détectés. Format :

```
[type]: [description courte en français]

[détails optionnels si le changement est complexe]
```

Types disponibles : `init`, `feat`, `update`, `fix`, `docs`, `config`, `refactor`

Exemple :

```
feat: ajout de la structure livrables/ et gestion des secrets
```

Propose-moi le message et demande validation :

```
Message de commit proposé :
"[message]"

Je valide ce message ? (ou propose une alternative)
```

### Étape 4 : Exécuter le commit

Une fois validé, exécute dans l'ordre :

```bash
git add -A
git status
git commit -m "[message validé]"
```

Affiche la confirmation de Git, puis annonce :

```
Commit effectué. Voici le résumé :
- [N] fichier(s) sauvegardé(s)
- Message : "[message]"
- Hash : [hash court du commit]

Ton workspace est sauvegardé localement. Pour pousser sur GitHub, tu peux me demander /push.
```

---

## Règles importantes

- Ne jamais stager `.env` ou tout fichier exclu par `.gitignore`. Si `git status` les montre comme "untracked" malgré le `.gitignore`, stoppe et signale le problème.
- Ne jamais utiliser `git add .` sans vérifier d'abord `git status` : toujours inspecter avant de stager.
- Toujours demander validation du message de commit avant d'exécuter.
- Si c'est le premier commit du dépôt, utilise le type `init` et propose un message du type : `init: mise en place du workspace Jarvis`.
- Communication en français, pas de tirets longs (em dashes).
