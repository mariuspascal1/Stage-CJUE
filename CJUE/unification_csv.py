"""import os
import pandas as pd
import re

# === PARAMÈTRES ===
classification = 'penal'
DOSSIER_CSV = 'corpus_update/v3/'+classification  # Dossier contenant les batchs
FICHIER_SORTIE = 'corpus_update/v3/'+classification+'/corpusv4.csv'  # Fichier final 1 ligne par arrêt
FICHIER_EXPLOSE = 'corpus_update/v3/'+classification+'/corpusv4_1.csv'  # Fichier final 1 ligne par texte interprété

# Colonnes fixes à conserver
COLONNES_FIXES = [
    "Numéro d’affaire", "Nom des parties", "Matières", "Indicateur", 
    "Dispositif", "Fondement", "Texte_environnant", "Date", "Lien", "Extraction"
]

# === Fonction d’extraction des textes interprétés ===
def extraire_textes(text):
    if pd.isna(text):
        return []
    # Couper à FIN
    match = re.search(r'^(.*?)(\bFIN\b)', text, flags=re.DOTALL)
    if not match:
        extrait = text
    else:
        extrait = match.group(1)

    # Extraire les textes interprétés
    lignes = re.findall(r'-Texte interprété\s*:\s*(.*)', extrait)
    return [f"{ligne.strip()}" for ligne in lignes if ligne.strip()]

# === RASSEMBLER TOUS LES BATCHS ===
fichiers_batch = sorted([
    f for f in os.listdir(DOSSIER_CSV) 
    if f.startswith("batch_") and f.endswith(".csv")
])

dfs = []
max_textes = 0

for f in fichiers_batch:
    chemin_fichier = os.path.join(DOSSIER_CSV, f)
    print(f"🔄 Chargement de : {chemin_fichier}")
    df = pd.read_csv(chemin_fichier)

    # Appliquer la fonction d'extraction
    df["__textes_list__"] = df["Extraction"].apply(extraire_textes)
    max_textes_batch = df["__textes_list__"].apply(len).max()
    max_textes = max(max_textes, max_textes_batch)

    dfs.append(df)

# === CONCATÉNATION ===
df_final = pd.concat(dfs, ignore_index=True)

# === Création des colonnes "Texte interprété n" ===
colonnes_textes = []
for i in range(max_textes):
    col_name = f"Texte interprété {i+1}"
    colonnes_textes.append(col_name)
    df_final[col_name] = df_final["__textes_list__"].apply(
        lambda lst: lst[i] if i < len(lst) else None
    )

# === Nettoyage intermédiaire ===
df_final.drop(columns=["__textes_list__"], inplace=True)

# === Filtrage des colonnes pour le 1er fichier ===
colonnes_finales = COLONNES_FIXES + colonnes_textes
colonnes_disponibles = [col for col in colonnes_finales if col in df_final.columns]
df_final = df_final[colonnes_disponibles]

# === Sauvegarde du fichier "1 ligne par arrêt" ===
df_final.to_csv(FICHIER_SORTIE, index=False)
print(f"✅ Corpus 1 ligne/arrêt sauvegardé sous : {FICHIER_SORTIE}")

# === Construction du fichier "1 ligne par texte interprété" ===
colonnes_identité = [col for col in df_final.columns if not col.startswith("Texte interprété")]

rows = []
for _, row in df_final.iterrows():
    textes = [row[col] for col in colonnes_textes if pd.notna(row[col])]
    for texte in textes:
        nouvelle_ligne = row[colonnes_identité].to_dict()
        nouvelle_ligne["Texte interprété"] = texte
        rows.append(nouvelle_ligne)

df_explose = pd.DataFrame(rows)

# === Sauvegarde du fichier "explosé" ===
df_explose.to_csv(FICHIER_EXPLOSE, index=False)
print(f"✅ Corpus 1 ligne/texte interprété sauvegardé sous : {FICHIER_EXPLOSE}")
"""

import os
import pandas as pd
import re

# === PARAMÈTRES ===
classification = 'penal'
DOSSIER_CSV = 'corpus_update/v4/'+classification  
FICHIER_SORTIE = 'corpus_update/v4/'+classification+'/corpusv4.csv'  
FICHIER_EXPLOSE = 'corpus_update/v4/'+classification+'/corpusv4_1.csv'  

# Colonnes fixes
COLONNES_FIXES = [
    "Numéro d’affaire", "Nom des parties", "Matières", "Indicateur", 
    "Dispositif", "Fondement", "Texte_environnant", "Date", "Lien", "Extraction"
]

# === Fonction extraction ===
def extraire_textes(text):
    if pd.isna(text):
        return []
    match = re.search(r'^(.*?)(\bFIN\b)', text, flags=re.DOTALL)
    extrait = match.group(1) if match else text
    lignes = re.findall(r'-Texte interprété\s*:\s*(.*)', extrait)
    return [ligne.strip() for ligne in lignes if ligne.strip()]

# === RASSEMBLER TOUS LES CSV ===
fichiers_batch = sorted([
    f for f in os.listdir(DOSSIER_CSV) if f.startswith("batch_") and f.endswith(".csv")
])

# si aucun fichier "batch_*" trouvé → prendre tous les csv du dossier
if not fichiers_batch:
    fichiers_batch = [f for f in os.listdir(DOSSIER_CSV) if f.endswith(".csv")]

dfs = []
max_textes = 0

for f in fichiers_batch:
    chemin_fichier = os.path.join(DOSSIER_CSV, f)
    print(f"🔄 Chargement de : {chemin_fichier}")
    df = pd.read_csv(chemin_fichier)

    df["__textes_list__"] = df["Extraction"].apply(extraire_textes)
    max_textes_batch = df["__textes_list__"].apply(len).max()
    max_textes = max(max_textes, max_textes_batch)

    dfs.append(df)

# === CONCATÉNATION ===
df_final = pd.concat(dfs, ignore_index=True)

# === Création des colonnes "Texte interprété n" ===
colonnes_textes = []
for i in range(max_textes):
    col_name = f"Texte interprété {i+1}"
    colonnes_textes.append(col_name)
    df_final[col_name] = df_final["__textes_list__"].apply(
        lambda lst: lst[i] if i < len(lst) else None
    )

# === Nettoyage intermédiaire ===
df_final.drop(columns=["__textes_list__"], inplace=True)

# === Filtrage des colonnes pour le 1er fichier ===
colonnes_finales = COLONNES_FIXES + colonnes_textes
colonnes_disponibles = [col for col in colonnes_finales if col in df_final.columns]
df_final = df_final[colonnes_disponibles]

# === Sauvegarde du fichier "1 ligne par arrêt" ===
df_final.to_csv(FICHIER_SORTIE, index=False)
print(f"✅ Corpus 1 ligne/arrêt sauvegardé sous : {FICHIER_SORTIE}")

# === Construction du fichier "1 ligne par texte interprété" ===
colonnes_identité = [col for col in df_final.columns if not col.startswith("Texte interprété")]

rows = []
for _, row in df_final.iterrows():
    textes = [row[col] for col in colonnes_textes if pd.notna(row[col])]
    for texte in textes:
        nouvelle_ligne = row[colonnes_identité].to_dict()
        nouvelle_ligne["Texte interprété"] = texte
        rows.append(nouvelle_ligne)

df_explose = pd.DataFrame(rows)

# === Sauvegarde du fichier "explosé" ===
df_explose.to_csv(FICHIER_EXPLOSE, index=False)
print(f"✅ Corpus 1 ligne/texte interprété sauvegardé sous : {FICHIER_EXPLOSE}")