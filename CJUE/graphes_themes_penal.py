import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# === CHEMINS À REMPLIR ===
# ==========================
INPUT_CSV = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/corpus_update.csv"
OUT_DIR = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/graphiques"

# ==========================
# === PARAMÈTRES ===
# ==========================
SEP = ";"  # ton corpus est en ;
COL_THEME = "Thèmes se rapportant au pénal"
COL_SUB = "Sous-thèmes se rapportant au pénal"

TOP_N_THEMES = 25       # top thèmes affichés (le reste = "Autres")
TOP_N_SUBTHEMES = 25    # top sous-thèmes par thème (le reste = "Autres")

# séparateurs possibles dans les cellules (virgule, point-virgule, saut de ligne, /, |)
SPLIT_PATTERN = r"[;,/|\n]+"

def clean_token(x: str) -> str:
    x = str(x).strip()
    x = x.replace("\u00A0", " ")     # espaces insécables
    x = re.sub(r"\s+", " ", x)       # espaces multiples
    return x

def split_multi(cell: str) -> list[str]:
    """Découpe une cellule multi-valeurs en liste de tokens propres."""
    if cell is None:
        return []
    cell = str(cell).strip()
    if cell == "" or cell.lower() in {"nan", "none"}:
        return []
    parts = re.split(SPLIT_PATTERN, cell)
    parts = [clean_token(p) for p in parts if clean_token(p)]
    return parts

def safe_slug(name: str) -> str:
    """Nom de fichier safe."""
    name = clean_token(name)
    name = re.sub(r'[\\/*?:"<>|]+', "_", name)
    name = name.replace("’", "'")
    name = name[:120].strip() or "sans_nom"
    return name

def plot_bar(series_counts: pd.Series, title: str, out_path: str, top_n: int = 25):
    """Bar chart horizontal, top_n + 'Autres'."""
    series_counts = series_counts.sort_values(ascending=False)

    if len(series_counts) > top_n:
        top = series_counts.iloc[:top_n]
        autres = series_counts.iloc[top_n:].sum()
        series_plot = pd.concat([top, pd.Series({"Autres": autres})])
    else:
        series_plot = series_counts

    plt.figure()
    series_plot.sort_values().plot(kind="barh")  # tri visuel (petit en bas, grand en haut)
    plt.title(title)
    plt.xlabel("Nombre d’occurrences")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_CSV, sep=SEP, dtype=str, keep_default_na=False)

    # --- 1) Comptage global des thèmes ---
    all_themes = []
    for v in df[COL_THEME].tolist():
        all_themes.extend(split_multi(v))

    s_themes = pd.Series(all_themes, dtype="string")
    themes_counts = s_themes.value_counts()

    # Export table
    themes_counts.to_csv(os.path.join(OUT_DIR, "themes_counts.csv"), sep=";", encoding="utf-8")

    # Graph global
    plot_bar(
        themes_counts,
        title=f"Répartition des thèmes (n={len(df)})",
        out_path=os.path.join(OUT_DIR, "themes_repartition.png"),
        top_n=TOP_N_THEMES
    )

    # --- 2) Pour chaque thème : répartition des sous-thèmes ---
    # Pré-calcul : listes de thèmes / sous-thèmes par ligne
    df["_themes_list"] = df[COL_THEME].apply(split_multi)
    df["_sub_list"] = df[COL_SUB].apply(split_multi)

    # Option : itérer sur les thèmes les plus fréquents (sinon ça peut faire 200 graphes)
    for theme in themes_counts.index.tolist():
        theme_slug = safe_slug(theme)

        # lignes où ce thème est présent
        mask = df["_themes_list"].apply(lambda lst: theme in lst)
        df_theme = df.loc[mask].copy()

        # collecte sous-thèmes
        subs = []
        for lst in df_theme["_sub_list"].tolist():
            subs.extend(lst)

        subs_counts = pd.Series(subs, dtype="string").value_counts()

        # si aucun sous-thème renseigné pour ce thème, on skip proprement
        if subs_counts.empty:
            continue

        # Export table
        subs_counts.to_csv(
            os.path.join(OUT_DIR, f"sousthemes_counts__{theme_slug}.csv"),
            sep=";",
            encoding="utf-8"
        )

        # Graph
        plot_bar(
            subs_counts,
            title=f"Sous-thèmes pour le thème : {theme} (n_lignes={len(df_theme)})",
            out_path=os.path.join(OUT_DIR, f"sousthemes__{theme_slug}.png"),
            top_n=TOP_N_SUBTHEMES
        )

    # Nettoyage colonnes temporaires (si tu veux sauvegarder df ensuite)
    df.drop(columns=["_themes_list", "_sub_list"], inplace=True)

    print("OK ✅")
    print(f"- Dossier sortie : {OUT_DIR}")
    print(f"- Graph global   : themes_repartition.png")
    print(f"- Tables         : themes_counts.csv + sousthemes_counts__*.csv")
    print(f"- Graphs         : sousthemes__*.png")

if __name__ == "__main__":
    main()
