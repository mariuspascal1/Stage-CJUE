'''import pandas as pd

# --- fichiers ---
corpus_file = "corpusv14/penal/corpusv14_mergev2.csv"
textes_file = "corpusv14/penal/liste_textes_interpretesv7.csv"
output_file = "corpusv14/penal/corpusv14_mergev3.csv"

# Charger les deux CSV
df = pd.read_csv(corpus_file, sep=',')
textes = pd.read_csv(textes_file, sep=';')

# Nettoyage éventuel des colonnes
textes.columns = textes.columns.str.strip()
df.columns = df.columns.str.strip()

# Récupérer les textes marqués "oui" dans le fichier de référence
penal_textes = textes.loc[
    textes["Relatif au pénal"].str.strip().str.lower() == "oui",
    "Texte interprété"
].dropna().unique()

# Créer une nouvelle colonne dans le corpus, initialisée vide
df["Relatif au pénal"] = ""

# Marquer "oui" pour les textes correspondants
df.loc[df["Texte interprété"].isin(penal_textes), "Relatif au pénal"] = "oui"

# Sauvegarde
df.to_csv(output_file, index=False)

print(f"✅ Colonne 'Relatif au pénal' ajoutée et marquée, fichier sauvegardé sous {output_file}")
'''

# Attention, il y a eu trois erreurs pour le gravite autour du pénal.

import pandas as pd

# --- fichiers ---
corpus_file = "corpus_update/v7/corpus.csv"
textes_file = "corpus_update/v7/liste_textes_interpretes.csv"
output_file = "corpus_update/v8/corpus.csv"

# Charger les deux CSV
df = pd.read_csv(corpus_file, sep=',')
textes = pd.read_csv(textes_file, sep=';')

# Nettoyage éventuel des colonnes
df.columns = df.columns.str.strip()
textes.columns = textes.columns.str.strip()

# On construit un dictionnaire Texte interprété -> Relatif au pénal
mapping = dict(zip(textes["Texte interprété"], textes["Relatif au pénal"]))

# Définir la priorité
priorite = {"pénal pur": 2, "gravite autour du pénal": 1, "non": 0}

# Fonction pour attribuer la bonne catégorie selon les textes présents
def attribuer_categorie(textes_str):
    if pd.isna(textes_str) or textes_str.strip() == "":
        return ""
    textes_list = [t.strip() for t in textes_str.split(";")]
    categories = [mapping.get(t, "non") for t in textes_list]  # par défaut "non" si inconnu
    # Garder la catégorie la plus haute selon l'ordre défini
    return max(categories, key=lambda c: priorite.get(c, -1))

# Appliquer au corpus
df["Relatif au pénal"] = df["Texte interprété"].apply(attribuer_categorie)

# Sauvegarde
df.to_csv(output_file, index=False)

print(f"✅ Colonne 'Relatif au pénal' ajoutée avec recopie et hiérarchie, fichier sauvegardé sous {output_file}")
