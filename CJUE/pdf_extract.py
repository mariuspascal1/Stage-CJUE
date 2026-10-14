import requests
import os
from pdfminer.high_level import extract_text
import re
import pandas as pd

corpusv1 = "/Users/mariuspascal/Desktop/CJUE/corpusv1/"
corpusv2 = "/Users/mariuspascal/Desktop/CJUE/corpusv2/"
corpus_textes = "/Users/mariuspascal/Desktop/CJUE/corpus_textes/"

count = 1

while count < 100:

    print(f"Traitement de la page {count}")
    df = pd.read_csv(corpusv1+"corpus_page_"+str(count)+".csv")
    
    for index, rows in df.iterrows():
        est_pdf = str(rows.get("Est_pdf", "")).lower() #On s'assure de travailler en minusclule

        if est_pdf == 'oui':
            url = rows['Lien']
            
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
            except Exception as e:
                print(f"Erreur pour l'URL {url} : {e}")
                continue

            pdf_path = "document.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)


            text = extract_text(pdf_path)
            #print(text)

            base_nom = rows["Type"].replace(":", "_") + ".txt"

            txt_path = corpus_textes+"page "+str(count)+"/"+base_nom

            page_folder = os.path.join(corpus_textes, f"page {count}/")
            os.makedirs(page_folder, exist_ok=True)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            os.remove(pdf_path)

            df.at[index, 'Fichier texte'] = base_nom


    # Sauvegarde CSV
    df.to_csv(corpusv2+"corpus_page_"+str(count)+".csv", index=False, encoding="utf-8")
    print(f"Page {count} traitée, csv enregistré.")
    count += 1
