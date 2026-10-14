'''import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://curia.europa.eu/juris/documents.jsf?page=99&nat=or&mat=or&pcs=Oor&jur=C&for=&jge=&dates=&language=fr&pro=&cit=none%252CC%252CCJ%252CR%252C2008E%252C%252C%252C%252C%252C%252C%252C%252C%252C%252Ctrue%252Cfalse%252Cfalse&oqp=&td=%3B%3B%3BPUB1%3BNPUB1%3B%3B%3BORDALL&avg=&lgrec=fr&text=p%25C3%25A9nal%252C%2Bp%25C3%25A9nale%252C%2Bp%25C3%25A9nales&lg=&cid=4216802"
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "lxml")

# Trouve la div tabber
tabber = soup.find("div", class_="tabber")

if not tabber:
    print("Aucune div.tabber trouvée.")
else:
    print("div.tabber trouvée.")

    # Affiche juste le HTML de la première ligne du tableau
    table = tabber.find("table")
    # ...
if table:
    trs = table.find_all("tr")
    if len(trs) > 1:
        print("Deuxièem ligne du tableau (première ligne de données) :")
        print(trs[13].prettify())  # Index 1 = deuxième <tr>, généralement le premier résultat
        print("Nombre total de lignes dans le tableau :")
        print(len(trs))
    else:
        print("Moins de deux lignes dans le tableau.")
else:
    print("Aucun tableau trouvé dans div.tabber.")

'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

output_dir = "corpus_update/"

url_prefix = """https://curia.europa.eu/juris/documents.jsf?nat=or&mat=or&pcs=Oor&jur=C&for=&jge=&dates=%2524type%253Dpro%2524mode%253DfromTo%2524from%253D2025.06.25%2524to%253D2025.09.04&language=fr&pro=&cit=none%252CC%252CCJ%252CR%252C2008E%252C%252C%252C%252C%252C%252C%252C%252C%252C%252Ctrue%252Cfalse%252Cfalse&oqp=&td=%3B%3B%3BPUB1%3BNPUB1%3B%3B%3BORDALL&avg=&lgrec=fr&page="""
url_suffix = """&text=p%25C3%25A9nal%252C%2Bp%25C3%25A9nale%252C%2Bp%25C3%25A9nales&lg=&cid=16683771"""

count = 1

while count<2:
    url = url_prefix+str(count)+url_suffix
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # Trouver la div contenant le tableau de résultats
    tabber = soup.find("div", class_="tabber")
    if not tabber:
        print("Aucune div.tabber trouvée.")
        exit()

    table = tabber.find("table", class_="detail_table_documents")
    if not table:
        print("Aucun tableau trouvé.")
        exit()

    # Toutes les lignes de décisions
    rows = table.find_all("tr", class_="table_document_ligne")

    # Extraction
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        numero_affaire = cols[0].get_text(strip=True)
        type_doc = cols[1].get_text(strip=True)
        date = cols[2].get_text(strip=True)
        nom = cols[3].get_text(strip=True)

        # Extraction spécifique des matières sans doublons
        mat_cell = cols[4]
        matieres_spans = mat_cell.find_all("span", class_="tooltipLink")
        matieres = []
        for span in matieres_spans:
            text = span.get_text(strip=True)
            if text and text not in matieres:
                matieres.append(text)
        matieres_str = ", ".join(matieres)

        # Lien HTML
        lien = None
        for a_tag in cols[5].find_all("a", href=True):
            href = a_tag["href"]
            if "doclang=fr" in href:
                lien = href
                break  # on sort dès qu'on trouve le premier lien en français


        data.append({
            "Numéro": numero_affaire,
            "Type": type_doc,
            "Date": date,
            "Nom": nom,
            "Matières": matieres_str,
            "Lien": lien
        })


    # Création du DataFrame
    df = pd.DataFrame(data)

    # Affichage
    #print(df) 

    # Export CSV si besoin
    df.to_csv(output_dir+"corpus_page_"+str(count)+".csv", index=False)

    print(f"page {count} extraite. {len(data)} documents ajoutés")

    # Page suivante 
    count += 1


