import pandas as pd
import os


csv_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/"
csv_pdf_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/detection pdf/"

count = 1
while count<2:
    df = pd.read_csv(csv_directory+"corpus_page_"+str(count)+".csv")

    # Préparer une liste pour stocker les lignes enrichies
    rows = []

    for index, row in df.iterrows():
        url = row["Lien"]
        if 'showPdf' in url:
            new_row=row.to_dict()
            new_row['Est_pdf']='oui'
        else:
            new_row=row.to_dict()
            new_row['Est_pdf']='non'

        rows.append(new_row)


    # Créer le nouveau DataFrame enrichi
    df_final = pd.DataFrame(rows)

    # Sauvegarde CSV
    df_final.to_csv(csv_pdf_directory+"corpus_page_"+str(count)+".csv", index=False, encoding="utf-8")
    print("Fichier stocké dans "+csv_pdf_directory+"corpus_page_"+str(count)+".csv")
    count += 1