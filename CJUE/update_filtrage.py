import pandas as pd

# ==========================
# === CHEMINS À REMPLIR ===
# ==========================
INPUT_MAIN_FILE = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/corpus_infocuria_api.csv"

EXCLUDE_FILE_1 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v9/nonpenalv13.csv"
EXCLUDE_FILE_2 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v9/penal.csv"
EXCLUDE_FILE_3 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v9/règlement de procédure.csv"
EXCLUDE_FILE_4 = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v9/corpus.csv"

OUTPUT_FILE = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/corpus_page_1.csv"

# séparateurs connus d'après tes prints
SEP_MAIN = ","          # corpus_infocuria_api.csv
SEP_EX1 = ","           # nonpenalv13.csv
SEP_EX2 = ";"           # penal.csv
SEP_EX3 = ";"           # règlement de procédure.csv
SEP_EX4 = ","           # corpus.csv

# colonnes possibles (selon fichiers)
CASE_COL_CANDIDATES = ["Numéro d'affaire", "Numéro d’affaire"]


def normalize_case_number(value: object) -> str:
    """
    Normalisation légère :
    - strip
    - uppercase
    - supprime espaces multiples
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip().upper()
    s = " ".join(s.split())
    return s


def find_case_column(df: pd.DataFrame, file_path: str) -> str:
    """Trouve la colonne 'numéro d'affaire' en gérant apostrophes différentes."""
    for c in CASE_COL_CANDIDATES:
        if c in df.columns:
            return c
    raise ValueError(
        f"❌ Colonne numéro d'affaire introuvable dans {file_path}. "
        f"Colonnes dispo: {list(df.columns)}"
    )


def load_exclusion_set(file_path: str, sep: str) -> set[str]:
    """Charge un fichier d'exclusion et retourne un set d'affaires normalisées."""
    df = pd.read_csv(file_path, sep=sep)
    case_col = find_case_column(df, file_path)
    return set(df[case_col].dropna().map(normalize_case_number))


def main():
    # === Chargement fichier principal ===
    df_main = pd.read_csv(INPUT_MAIN_FILE, sep=SEP_MAIN)
    main_case_col = find_case_column(df_main, INPUT_MAIN_FILE)

    df_main["_case_norm"] = df_main[main_case_col].map(normalize_case_number)

    # === Chargement exclusions ===
    exclusion_set = set()
    exclusion_set |= load_exclusion_set(EXCLUDE_FILE_1, SEP_EX1)
    exclusion_set |= load_exclusion_set(EXCLUDE_FILE_2, SEP_EX2)
    exclusion_set |= load_exclusion_set(EXCLUDE_FILE_3, SEP_EX3)
    exclusion_set |= load_exclusion_set(EXCLUDE_FILE_4, SEP_EX4)

    # enlève éventuellement "" du set
    exclusion_set.discard("")

    print(f"➡️ {len(exclusion_set)} numéros d'affaire à exclure")

    # === Filtrage ===
    df_filtered = df_main[~df_main["_case_norm"].isin(exclusion_set)].copy()
    df_filtered.drop(columns=["_case_norm"], inplace=True)

    # === Export ===
    df_filtered.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"✅ OK : {len(df_filtered)} affaires conservées.")
    print(f"📁 Fichier exporté : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
