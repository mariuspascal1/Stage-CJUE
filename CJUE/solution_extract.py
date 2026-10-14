import os
import re
import pandas as pd


corpusv3 = "/Users/mariuspascal/Desktop/CJUE/corpusv3/"
corpusv4 = "/Users/mariuspascal/Desktop/CJUE/corpusv4/"
corpus_texte = "/Users/mariuspascal/Desktop/CJUE/corpus_textes/"

# ======= Motif de recherche pour les documents qui ne sont pas pdf =======
solution_re = re.compile(
                r"par\s+ces\s+motifs,.*?(?=(Ainsi\s+jugé|Ainsi\s+fait|Ainsi\s+prononcé|Signatures))",
                re.IGNORECASE | re.DOTALL
            )

indicateur_re = re.compile(r"[«\"](.*?)[»\"]", re.DOTALL)

# ======= Motif de recherche pour les documents qui sont pdf =======
# Pas d'indicateur dans ce cas là
solution_pdf_re = re.compile(
    r"Sur\s+les\s+dépens.*?(?=(Ainsi\s+jugé|Ainsi\s+fait|Ainsi\s+prononcé|Signatures))",
    re.IGNORECASE | re.DOTALL
)

df = pd.read_csv(corpusv3+"corpusv3bis.csv", sep = ';')


for index, row in df.iterrows():
    est_pdf = str(row.get("Est_pdf", "")).lower() #On s'assure de travailler en minusclule

    if pd.isna(row['Dispositif']): # Vérifie si le dispositif est vide
        nom_fichier = corpus_texte + "page " + str(row['Page']) + "/" + str(row['Fichier texte'])
        #print(nom_fichier)

        if est_pdf == 'non':
            with open(nom_fichier, "r", encoding="utf-8") as f:
                texte = f.read()  
                #print(texte)

                # Extraire le dispositif
                match_dispositif = solution_re.search(texte)
                dispositif = match_dispositif.group(0).strip() if match_dispositif else ""

                # Extraire indicateur
                match_indicateur = indicateur_re.search(texte)
                indicateur = match_indicateur.group(1).strip() if match_indicateur else ""


                #print("Dispositif extrait :", dispositif)
                df.at[index, "Dispositif"] = dispositif
                #print("Indicateurs extraits :", indicateur)
                df.at[index, "Indicateur"] = indicateur
                if pd.isna(dispositif) or not dispositif:
                    print(f"Dispositif non extrait pour l'arrêt {row['Numéro']}.")
                if pd.isna(indicateur) or indicateur:
                    print(f"Indicateur non extrait pour l'arrêt {row['Numéro']}.")

        else:
            with open(nom_fichier, "r", encoding="utf-8") as f:
                texte = f.read()  
                #print(texte)

                # Extraire le dispositif
                match_dispositif = solution_pdf_re.search(texte)
                dispositif = match_dispositif.group(0).strip() if match_dispositif else ""

                df.at[index, "Dispositif"] = dispositif

                if pd.isna(dispositif) or not dispositif:
                    print(f"Dispositif non extrait pour l'arrêt {row['Numéro']}.")


# Sauvegarde CSV
df.to_csv(corpusv4+"corpusv4.csv", index=False, encoding="utf-8")
print(f"csv enregistré à "+corpusv4+"corpusv4.csv .")

