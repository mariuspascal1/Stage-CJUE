import pandas as pd

#============ Première classification ============
input_dir = "/Users/mariuspascal/Desktop/CJUE/corpusv4/"
input_file = "corpusv4.csv"
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpusv7/"
output_file = "corpusv7.csv"

#============ Deuxième classification ============
input_dir = "/Users/mariuspascal/Desktop/CJUE/corpusv7/"
input_file = "corpusv7.csv"
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpusv8/"
output_file = "corpusv8.csv"

#============ Troisième classification ============
input_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v1/"
input_file = "corpus.csv"
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_update/v2/"
output_file = "corpus.csv"

#============ Quatrière classification ============
input_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v1/"
input_file = "corpus.csv"
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v2/"
output_file = "corpus.csv"

# === 1. Charger les mots-clés depuis un fichier texte ===
def load_keywords_from_txt(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

keywords1 = load_keywords_from_txt("keywords/mots_cles_penal1.txt")
keywords2 = load_keywords_from_txt("keywords/mots_cles_penal2.txt")
keywords = keywords1 + keywords2

# === 2. Charger ton CSV ===
df = pd.read_csv(input_dir + input_file)

# === 3. Vérifier si un mot-clé est contenu dans l’indicateur
def contient_mot_clef(indicateur, keywords):
    if not isinstance(indicateur, str):
        return False
    indicateur_lower = indicateur.lower()
    return any(kw in indicateur_lower for kw in keywords)

# === 4. Marquer les lignes pénales (seulement celles non encore marquées)
if "Est_penal" not in df.columns:
    df["Est_penal"] = False  # Initialise la colonne si elle n'existe pas

df.loc[~df["Est_penal"], "Est_penal"] = df.loc[~df["Est_penal"], "Indicateur"].apply(
    lambda x: contient_mot_clef(x, keywords)
)

# === 5. Séparer et sauvegarder
df[df["Est_penal"]].to_csv(output_dir + "indicateurs_penal.csv", index=False)
df[~df["Est_penal"]].to_csv(output_dir + "indicateurs_non_penal.csv", index=False)
df.to_csv(output_dir + output_file, index=False)

print("✅ Fichiers créés : indicateurs_penal.csv / indicateurs_non_penal.csv")
