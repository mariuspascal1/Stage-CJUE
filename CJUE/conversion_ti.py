'''import pandas as pd

# Charger le fichier CSV
df = pd.read_csv("corpusv14/penal/corpusv14_explodev2.csv", sep=',')

# Sélectionner toutes les colonnes qui commencent par "Texte interprété"
colonnes_interpretes = [col for col in df.columns if col.lower().startswith("texte interprété")]

# Créer la nouvelle colonne fusionnée
def fusionner_textes(row):
    valeurs = [str(row[col]).strip() for col in colonnes_interpretes if pd.notna(row[col]) and str(row[col]).strip() != ""]
    return "; ".join(sorted(set(valeurs))) if valeurs else ""

df["Texte interprété"] = df.apply(fusionner_textes, axis=1)

# Sauvegarder le nouveau fichier
df.to_csv("corpusv14/penal/corpusv14_mergev2.csv", index=False)

print("Fichier sauvegardé sous corpusv14v3.csv")
'''

'''import pandas as pd

# --- fichiers ---
input_file = "corpusv14/penal/corpusv14_explodev2.csv"
output_file = "corpusv14/penal/corpusv14_mergev2.csv"

# Charger le fichier CSV (forme 1 : explosée)
df = pd.read_csv(input_file, sep=",")

# Vérifier la présence des colonnes attendues
if "Numéro d’affaire" not in df.columns or "Texte interprété" not in df.columns:
    raise ValueError("Le fichier doit contenir au moins 'Numéro d'affaire' et 'Texte interprété'.")

# Grouper par affaire et fusionner les textes interprétés
df_grouped = (
    df.groupby("Numéro d’affaire", dropna=False)
    .agg(lambda x: "; ".join(sorted(set(str(v).strip() for v in x if pd.notna(v) and str(v).strip() != ""))))
    .reset_index()
)

# Si tu veux garder les autres colonnes de l'affaire (ex : Date, Formation, etc.)
# on peut récupérer la première valeur non nulle de chaque colonne :
other_cols = [col for col in df.columns if col not in ["Texte interprété"]]
df_full = (
    df[other_cols]
    .drop_duplicates(subset=["Numéro d’affaire"])
    .merge(df_grouped, on="Numéro d’affaire", how="left")
)

# Sauvegarder le fichier fusionné (forme 2 : une ligne par arrêt)
df_full.to_csv(output_file, index=False)

print(f"✅ Conversion terminée : {len(df_full)} arrêts sauvegardés dans {output_file}")
'''

import pandas as pd

# --- fichiers ---
input_file = "corpus_update/v6/corpus1.csv"
output_file = "corpus_update/v7/corpus.csv"

# Charger le fichier CSV (forme 1 : explosée)
df = pd.read_csv(input_file, sep=";")

# Nettoyer les noms de colonnes (pour éviter espaces ou caractères invisibles)
df.columns = df.columns.str.strip().str.replace("\u00A0", " ", regex=True)

# Identifier la colonne affaire
affaire_col = next(col for col in df.columns if "Numéro" in col and "affaire" in col)

# Grouper par affaire et fusionner les textes interprétés
df_grouped = (
    df.groupby(affaire_col, dropna=False)["Texte interprété"]
    .apply(lambda x: "; ".join(sorted(set(str(v).strip() for v in x if pd.notna(v) and str(v).strip() != ""))))
    .reset_index()
)

# Récupérer les autres colonnes (première valeur non nulle par affaire)
other_cols = [col for col in df.columns if col not in ["Texte interprété"]]
df_meta = df[other_cols].drop_duplicates(subset=[affaire_col])

# Fusion propre sans créer de doublons
df_full = df_meta.merge(df_grouped, on=affaire_col, how="left")

# Sauvegarder le fichier fusionné (forme 2 : une ligne par arrêt)
df_full.to_csv(output_file, index=False)

print(f"✅ Conversion terminée : {len(df_full)} arrêts sauvegardés dans {output_file}")
