import pandas as pd

# ==========================
# === CHEMINS À REMPLIR ===
# ==========================
INPUT_1 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/penal.csv"
INPUT_2 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/penal_helene.csv"
INPUT_3 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/non_penal.csv"
OUTPUT  = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3/corpus_update.csv"

MAJ_VALUE = "18/02/2026"

# Colonnes attendues dans le CSV 2 (ordre strict) + MAJ à ajouter
COLONNES_CSV2 = [
    "Numéro d'affaire",
    "Nom des parties",
    "Date",
    "Lien",
    "Texte interprété",
    "Classification",
    "Sous-classification",
    "Relatif au pénal",
    "Dispositif",
    "Indicateur",
    "Matières",
    "Thèmes se rapportant au pénal",
    "Sous-thèmes se rapportant au pénal",
]

COLONNES_FIXES_DF1 = ["Numéro d'affaire", "Indicateur", "Dispositif", "Date", "Lien"]


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les noms de colonnes: trims + apostrophes typographiques."""
    df = df.copy()
    df.columns = [
        str(c).strip()
              .replace("’", "'")
              .replace("\u00A0", " ")  # espace insécable
        for c in df.columns
    ]
    return df


def main():
    # ---- Lecture ----
    df1 = pd.read_csv(INPUT_1, dtype=str, keep_default_na=False)           # généralement ","
    df2 = pd.read_csv(INPUT_2, dtype=str, keep_default_na=False, sep=";")  # chez toi ";"
    df3 = pd.read_csv(INPUT_3, dtype=str, keep_default_na=False) 

    df3 = df3[df3["Dispositif"]==""].copy()  # filtrer les pénal (si jamais présents) pour ne garder que les non-pénal

    # ---- Harmonisation noms de colonnes ----
    df1 = clean_columns(df1)
    df2 = clean_columns(df2)
    df3 = clean_columns(df3)

    # Debug utile
    print("df1:", list(df1.columns))
    print("df2:", list(df2.columns))
    print("df3:", list(df3.columns))
    print(df3.head())

    # ---- Vérif colonne clé ----
    if "Numéro d'affaire" not in df1.columns:
        raise ValueError("df1: colonne 'Numéro d'affaire' absente (après nettoyage).")
    if "Numéro d'affaire" not in df2.columns:
        raise ValueError("df2: colonne 'Numéro d'affaire' absente (après nettoyage).")
    if "Numéro d'affaire" not in df3.columns:
        raise ValueError("df3: colonne 'Numéro d'affaire' absente (après nettoyage).")
    # ---- 1) df1 et df3: garder colonnes fixes + MAJ ----
    for c in COLONNES_FIXES_DF1:
        if c not in df1.columns:
            df1[c] = ""

    df1 = df1[COLONNES_FIXES_DF1].copy()

    for c in COLONNES_FIXES_DF1:
        if c not in df3.columns:
            df3[c] = ""

    df3 = df3[COLONNES_FIXES_DF1].copy()
    df1["MAJ"] = MAJ_VALUE
    df3["MAJ"] = MAJ_VALUE



    # ---- 2) df2: garantir toutes les colonnes attendues + MAJ vide ----
    for c in COLONNES_CSV2:
        if c not in df2.columns:
            df2[c] = ""

    df2 = df2[COLONNES_CSV2].copy()
    df2["MAJ"] = ""  # anciens

    # ---- 3) Clé de comparaison: juste strip (pas de normalisation) ----
    df1["_key"] = df1["Numéro d'affaire"].astype(str).str.strip()
    df2["_key"] = df2["Numéro d'affaire"].astype(str).str.strip()
    df3["_key"] = df3["Numéro d'affaire"].astype(str).str.strip()

    # ---- 4) df1 et df3 au format df2 ----
    df1_full = pd.DataFrame("", index=df1.index, columns=COLONNES_CSV2 + ["MAJ"])
    df1_full["Numéro d'affaire"] = df1["Numéro d'affaire"]
    df1_full["Date"] = df1["Date"]
    df1_full["Lien"] = df1["Lien"]
    df1_full["Dispositif"] = df1["Dispositif"]
    df1_full["Indicateur"] = df1["Indicateur"]
    df1_full["MAJ"] = df1["MAJ"]
    df1_full["_key"] = df1["_key"]

    df3_full = pd.DataFrame("", index=df3.index, columns=COLONNES_CSV2 + ["MAJ"])
    df3_full["Numéro d'affaire"] = df3["Numéro d'affaire"]
    df3_full["Date"] = df3["Date"]
    df3_full["Lien"] = df3["Lien"]
    df3_full["Dispositif"] = df3["Dispositif"]
    df3_full["Indicateur"] = df3["Indicateur"]
    df3_full["MAJ"] = df3["MAJ"]
    df3_full["_key"] = df3["_key"]

    # ---- 5) Ajout seulement des nouveaux ----
    existing_keys = set(df2["_key"].tolist())
    df1_new = df1_full[~df1_full["_key"].isin(existing_keys)].copy()
    df3_new = df3_full[~df3_full["_key"].isin(existing_keys)].copy()
    df_final = pd.concat(
        [df2.drop(columns=["_key"]), df1_new.drop(columns=["_key"]), df3_new.drop(columns=["_key"])],
        ignore_index=True
    )

    # Export: on garde le même séparateur que df2 (chez toi ;)
    df_final.to_csv(OUTPUT, index=False, sep=";", encoding="utf-8")

    print("OK ✅")
    print(f"- Lignes df2 (existantes) : {len(df2)}")
    print(f"- Nouveaux ajoutés        : {len(df1_new)}")
    print(f"- Non-pénal ajoutés      : {len(df3_new)}")
    print(f"- Total exporté           : {len(df_final)}")
    print(f"Fichier : {OUTPUT}")


if __name__ == "__main__":
    main()
