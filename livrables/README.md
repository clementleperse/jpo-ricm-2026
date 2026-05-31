# Livrables

Ce dossier contient tout ce que Claude produit pour toi : sites web, applications, documents de travail, analyses, etc.

## Règle d'or

| Quoi | Où |
|------|----|
| **Inputs** — documents que tu fournis (PDFs, exports, notes, captures) | `context/import/` |
| **Outputs** — ce que Claude produit pour toi | `livrables/` |

## Structure

```
livrables/
├── site-web/       Sites et pages web générés
├── applications/   Applications, scripts et outils
├── RICM/           Travail dans le cadre du poste (SCAB, rapports, présentations)
├── Side-business/  Documents liés aux projets de business
└── divers/         Tout ce qui ne rentre pas ailleurs
```

## Convention de nommage

Format recommandé : `AAAA-MM-JJ_nom-court-descriptif/`

Exemples :
- `2026-05-31_landing-page-coaching/`
- `2026-06-15_rapport-inventaire-SCAB/`
- `2026-07_analyse-marche-formation-militaire/`

Pour les fichiers uniques (pas de dossier nécessaire) : même logique avec l'extension.
- `2026-05-31_analyse-concurrents.md`
- `2026-06-01_template-email-prospect.docx`

## Principe

Un livrable = un dossier ou fichier daté. Ça permet de retrouver n'importe quoi par date ou par mot-clé, et de voir l'historique de production au premier coup d'oeil.
