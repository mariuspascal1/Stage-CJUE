import pandas as pd

# Charger le CSV aplati (chaque ligne = un arrêt + un texte interprété)
df = pd.read_csv("corpus_update/v4/penal/corpusv4_1.csv", sep=",")

# Vérifie qu'on a bien la colonne attendue
if "Texte interprété" not in df.columns:
    raise ValueError("La colonne 'Texte interprété' est manquante dans le fichier.")

# Extraire tous les textes uniques
textes_uniques = df["Texte interprété"].dropna().str.strip().unique()

# Mettre dans un DataFrame pour pouvoir l’exporter
df_textes = pd.DataFrame({"Texte interprété": sorted(textes_uniques)})

# Sauvegarder pour correction manuelle
df_textes.to_csv("corpus_update/v4/penal/liste_textes_interpretes.csv", index=False)

print("✅ Liste des textes uniques sauvegardée dans liste_textes_interpretes.csv")
