# Stage-CJUE

Outils d'analyse de la jurisprudence de la Cour de justice de l'Union européenne (CJUE) en matière pénale, et de la manière dont la chambre criminelle de la Cour de cassation française la cite.

> **À compléter :** cadre du stage (structure d'accueil, période, encadrant·e), question de recherche et résultats attendus.

## Contenu

Le dépôt contient deux ensembles de scripts Python. D'après leur contenu, ils forment deux chaînes de traitement qui se croisent à la fin.

### `CJUE/` : constitution et classification d'un corpus d'arrêts de la CJUE

| Étape | Scripts |
|---|---|
| Collecte des arrêts (InfoCuria) | `scrap_tab.py`, `scrap_tab_v2.py` |
| Détection des PDF et extraction des textes | `detection_pdf.py`, `pdf_extract.py`, `extraction_textes.py`, `extraction_textesV2.py` |
| Extraction du dispositif et de l'indicateur | `solution_extract.py` |
| Repérage du pénal par mots-clés | `recherche_dispositifs.py`, `recherche_texte.py`, `keywords/` |
| Classification (matières, indicateur, textes interprétés) | `classification_matieres.py`, `classification_indicateur.py`, `liste_textes.py`, `relatif_penal.py`, `conversion_ti.py` |
| Fusion et mise à jour des corpus | `creer_corpus.py`, `merge.py`, `merge_update.py`, `unification_csv.py`, `update_filtrage.py` |
| Graphiques | `graphes_themes_penal.py`, `sous-categories.py` |

Certains scripts sont en partie commentés : ce sont d'anciennes versions conservées pour mémoire.

### `Chambre Criminelle/` : arrêts de la chambre criminelle (Légifrance) et citations de la CJUE

| Étape | Scripts |
|---|---|
| Recherche et téléchargement via l'API Légifrance (PISTE) | `search_legifrance.py`, `download_arrets_complets.py`, `update_arrets.py`, `find_arrets_manquants.py`, `test_proximité.py` |
| Filtrage par mots-clés | `filter_arrets_case_sensitive.py`, `keywords/` |
| Conversion JSON vers CSV et textes | `json_to_csv.py` |
| Extraction des références CJUE (format `C-150/88`) | `extract_cjue_refs.py` |
| Croisement avec le corpus CJUE | `croisement_citations_cjue.py`, `tableau_affaires_citees.py`, `camembert_corpus_vs_hors_corpus.py` |
| Statistiques et graphiques | `count_arret.py`, `bornes_dates_arrets.py`, `plot_arrets_par_annee.py`, `plot_arrets_par_annee_titre.py` |

## Installation

```bash
pip install -r requirements.txt
```

### Identifiants API Légifrance (PISTE)

Les scripts de `Chambre Criminelle/` utilisent l'API Légifrance via PISTE (environnement sandbox). Les identifiants ne sont pas dans le code :

1. Copier `.env.example` en `.env`.
2. Renseigner `PISTE_CLIENT_ID` et `PISTE_CLIENT_SECRET` (à obtenir sur le portail PISTE).

Le fichier `.env` est ignoré par git. Ne jamais le versionner.

## Utilisation

Les scripts de `Chambre Criminelle/` s'utilisent en ligne de commande. Exemple :

```bash
python "Chambre Criminelle/search_legifrance.py" \
  --keywords "Chambre Criminelle/keywords/mots_cles_UE.txt" \
  --output sortie/ --basename arrets
```

Chaque script décrit ses options avec `--help`.

## Limites connues

- Les corpus (CSV, JSON, textes d'arrêts) ne sont pas versionnés : ils sont à régénérer avec les scripts ou à fournir séparément.
- Plusieurs scripts de `CJUE/` contiennent des chemins absolus (`/Users/mariuspascal/Desktop/CJUE/...`) à adapter à ton environnement.
