import os
import re
import pandas as pd

corpusv2 = "/Users/mariuspascal/Desktop/CJUE/corpusv2/"
corpusv3 = "/Users/mariuspascal/Desktop/CJUE/corpusv3/"

count = 1

# Liste pour stocker les DataFrames
liste_df = []

while count < 100:
    print(f"Traitement de la page {count}.")

    chemin_csv = corpusv2 + "corpus_page_" + str(count) + ".csv"
    
    if os.path.exists(chemin_csv):
        df = pd.read_csv(chemin_csv)
        df['Page'] = count
        liste_df.append(df)

    count += 1

# Concaténer tous les DataFrames
df_final = pd.concat(liste_df, ignore_index=True)

# Supprimer les doublons
df_final = df_final.drop_duplicates()

# Sauvegarder le DataFrame final
df_final.to_csv(corpusv3 + "corpusv3.csv", index=False, encoding="utf-8")

print("Fichier final sauvegardé.")
