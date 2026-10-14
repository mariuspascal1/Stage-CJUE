import pandas as pd

# === Paramètres ===
fichier1 = "corpusv14/penal/corpusv14_mergev5.csv"
fichier2 = "corpus_update/v8/corpus.csv"
fichier_sortie = "corpus_update/v9/corpus.csv"

# === Chargement ===
df1 = pd.read_csv(fichier1)
df2 = pd.read_csv(fichier2)

# === Concaténation ===
df = pd.concat([df1, df2], ignore_index=True)

# === Suppression éventuelle de "Type de droit" ===
if "Type de droit" in df.columns:
    df = df.drop(columns=["Type de droit"])

# === Colonnes dans l’ordre voulu ===
ordre_colonnes = [
    "Numéro d’affaire",
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
]

# Vérifier les colonnes manquantes (pour éviter crash)
colonnes_existantes = [col for col in ordre_colonnes if col in df.columns]
df = df[colonnes_existantes]

# === Sauvegarde ===
df.to_csv(fichier_sortie, index=False)
print(f"✅ Corpus fusionné sauvegardé sous : {fichier_sortie}")
