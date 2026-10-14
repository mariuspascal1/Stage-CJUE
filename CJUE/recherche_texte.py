import pandas as pd
import os

# === 1. Charger les mots-clés depuis un fichier texte ===
def load_keywords_from_txt(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

keywords1 = load_keywords_from_txt("mots_cles_penal1.txt")
keywords2 = load_keywords_from_txt("mots_cles_penal2.txt")
keywords = keywords1 + keywords2

# === 2. Charger le CSV corpusv8 ===
input_path = "/Users/mariuspascal/Desktop/CJUE/corpusv8/corpusv8.csv"
df = pd.read_csv(input_path)

# === 3. Filtrer les lignes Est_pdf == "oui" ET Est_penal == False ===
df_pdf_candidates = df[
    (df["Est_pdf"].str.lower() == "oui") & 
    (df["Est_penal"] == False)
].copy()

# === 4. Fonction pour extraire les mots-clés présents dans un fichier texte ===
def extraire_mots_cles_trouves(file_path, keywords):
    if not os.path.isfile(file_path):
        return []
    try:
        with open(file_path, encoding="utf-8") as f:
            contenu = f.read().lower()
            return [kw for kw in keywords if kw in contenu]
    except Exception as e:
        print(f"Erreur lecture fichier {file_path}: {e}")
        return []

# === 5. Appliquer la détection sur les fichiers texte associés ===
base_text_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_textes/"

df_pdf_candidates["Mots_cles_trouves"] = df_pdf_candidates["Fichier texte"].apply(
    lambda nom_fichier: extraire_mots_cles_trouves(os.path.join(base_text_dir, nom_fichier), keywords)
)

# Mettre Est_penal à True si au moins un mot-clé est trouvé
df_pdf_candidates["Est_penal"] = df_pdf_candidates["Mots_cles_trouves"].apply(lambda lst: len(lst) > 0)

# === 6. Mettre à jour dans le DataFrame principal ===
df.loc[df_pdf_candidates.index, "Est_penal"] = df_pdf_candidates["Est_penal"]
df.loc[df_pdf_candidates.index, "Mots_cles_trouves"] = df_pdf_candidates["Mots_cles_trouves"]

# === 7. Sauvegardes ===
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpusv9/"
os.makedirs(output_dir, exist_ok=True)

df.to_csv(output_dir + "corpusv9.csv", index=False)
df[df["Est_pdf"].str.lower() == "oui"].to_csv(output_dir + "corpusv9pdf.csv", index=False)

print("✅ Fichiers enregistrés avec colonne 'Mots_cles_trouves' ajoutée.")
