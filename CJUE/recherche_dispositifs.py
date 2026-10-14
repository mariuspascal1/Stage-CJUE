import pandas as pd
import os

# === 1. Charger les mots-clés depuis un fichier texte ===
def load_keywords_from_txt(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

keywords1 = load_keywords_from_txt("keywords/mots_cles_penal1.txt")
keywords2 = load_keywords_from_txt("keywords/mots_cles_penal2.txt")
keywords = list(set(keywords1 + keywords2))  # éviter doublons

# === 2. Charger le CSV corpusv9 ===
input_path = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v2/corpus.csv"
df = pd.read_csv(input_path)

# === 3. Filtrer les lignes Est_penal == False ===
df_candidates = df[df["Est_penal"] == False].copy()

# === 4. Fonction pour extraire les mots-clés présents dans le champ "Dispositif" ===
def extraire_mots_cles_dans_dispositif(dispositif, keywords):
    if not isinstance(dispositif, str):
        return []
    dispositif = dispositif.lower()
    return [kw for kw in keywords if kw in dispositif]

# === 5. Appliquer la détection sur "Dispositif" ===
df_candidates["Mots_cles_trouves"] = df_candidates["Dispositif"].apply(
    lambda texte: extraire_mots_cles_dans_dispositif(texte, keywords)
)
"""
Je neutralise la partie Matière car je n'ai pas eu le temps d'extraire les matières dans la nouvelle MAJ

# === 5.b. Ajouter ceux avec "coopération judiciaire en matière pénale" dans Matières ===
mention = "coopération judiciaire en matière pénale"

def contient_mention_cooperation(matiere):
    if not isinstance(matiere, str):
        return False
    return mention in matiere.lower()

indices_coop = df_candidates[df_candidates["Matières"].apply(contient_mention_cooperation)].index

def ajout_mention_mots_cles(lst):
    if not isinstance(lst, list):
        lst = []
    if mention not in lst:
        return lst + [mention]
    return lst

df_candidates.loc[indices_coop, "Mots_cles_trouves"] = df_candidates.loc[indices_coop, "Mots_cles_trouves"].apply(
    ajout_mention_mots_cles
)
"""

# Mettre Est_penal à True si au moins un mot-clé est trouvé
df_candidates["Est_penal"] = df_candidates["Mots_cles_trouves"].apply(lambda lst: len(lst) > 0)

# === 6. Mettre à jour dans le DataFrame principal ===
df.loc[df_candidates.index, "Est_penal"] = df_candidates["Est_penal"]
df.loc[df_candidates.index, "Mots_cles_trouves"] = df_candidates["Mots_cles_trouves"]

# === 7. Sauvegardes ===
output_dir = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v3"
os.makedirs(output_dir, exist_ok=True)

df.to_csv(os.path.join(output_dir, "corpus.csv"), index=False)
df[df["Est_pdf"].str.lower() == "oui"].to_csv(os.path.join(output_dir, "corpusv11pdf.csv"), index=False)

# === 8. Séparer en deux CSV selon Est_penal ===
df_penal = df[df["Est_penal"] == True]
df_non_penal = df[df["Est_penal"] == False]

df_penal.to_csv(os.path.join(output_dir, "penal.csv"), index=False)
df_non_penal.to_csv(os.path.join(output_dir, "non_penal.csv"), index=False)


print("✅ Recherche effectuée dans la colonne 'Dispositif'. Fichiers enregistrés dans corpusv11.")
