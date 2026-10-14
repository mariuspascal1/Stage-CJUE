from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re
import time
import random

csv_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/"
textes_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/textes/"
csv_pdf_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/detection pdf/"
csv_v1_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v1/"

count = 1

while count<2:

    # Exemple de DataFrame avec une ligne
    df = pd.read_csv(csv_pdf_directory+"corpus_page_"+str(count)+".csv")

    # Préparer une liste pour stocker les lignes enrichiesÒ≈©
    rows = []

    for index, row in df.iterrows():
        est_pdf = str(row.get("Est_pdf", "")).lower() #On s'assure de travailler en minusclule

        # Initialisation des champs
        dispositif_text = ""
        indicateur_text = ""
        base_nom = ""

        if est_pdf == "oui":
            print(f"PDF détecté (non parsable HTML) pour l’URL : {row['Lien']}")

        else :
            url = row["Lien"]
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                time.sleep(random.randint(2,10))

                soup = BeautifulSoup(response.text, 'lxml')
                div = soup.find('div', id='document_content')

                if div:
                    if div.find('dl'):
                        print(f"Ancien format détecté pour l’URL : {url}")

                        texte_complet = div.get_text(separator="\n\n", strip=True)
                    
                    else : 

                        paragraphs = div.find_all('p')

                        texte_complet = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                        dispositifs = div.find_all('p', class_=re.compile("Dispositif"))
                        dispositif_text = '\n\n'.join(p.get_text(strip=True) for p in dispositifs)

                        indicateurs = div.find_all('p', class_='C71Indicateur')
                        indicateur_text = '\n\n'.join(p.get_text(strip=True) for p in indicateurs)

                    base_nom = row["Type"].replace(":", "_") + ".txt"
                    page_folder = os.path.join(textes_directory, f"page {count}/")
                    os.makedirs(page_folder, exist_ok=True)

                    with open(textes_directory+"page " + str(count) + "/" + base_nom, "w", encoding="utf-8") as f:
                        f.write(texte_complet)
                else:
                    print(f"Contenu non trouvé pour l’URL : {url}")

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération de l’URL : {url}\n -> {e}")


        # Ajouter les données à la ligne
        new_row = row.to_dict()
        new_row["Dispositif"] = dispositif_text
        new_row["Indicateur"] = indicateur_text
        new_row["Fichier texte"] = base_nom

        rows.append(new_row)

        

    # Créer le nouveau DataFrame enrichi
    df_final = pd.DataFrame(rows)

    # Sauvegarde CSV
    df_final.to_csv(csv_v1_directory+"corpus_page_"+str(count)+".csv", index=False, encoding="utf-8")
    #df_final.to_csv("/Users/mariuspascal/Desktop/CJUE/test/corpus_page_"+str(count)+".csv", index=False, encoding="utf-8")
    print(f"Page {count} traitée, csv enregistré.")
    count+=1
    time.sleep(20)


