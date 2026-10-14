from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re
import time
import random

# ==========================
# === PARAMÈTRES CHEMINS ===
# ==========================
textes_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/textes/"
csv_pdf_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/detection pdf/"
csv_v1_directory = "/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/v1/"

# ==========================
# === REPRISE ICI ===
# ==========================
START_AT_ROW = 520   # <-- 520 = reprend à l'affichage [521/...]
MAX_PAGES = 1

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def safe_filename(name: str) -> str:
    name = str(name or "").strip()
    if not name:
        name = "sans_nom"
    name = re.sub(r'[\\/*?:"<>|]+', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def get_container(soup: BeautifulSoup):
    return soup.select_one("#document_content") or soup.body

def extract_texts_from_container(container):
    if container is None:
        return "", "", "", False
    if container.find("dl"):
        texte_complet = container.get_text(separator="\n\n", strip=True)
        return texte_complet, "", "", True

    paragraphs = container.find_all("p")
    texte_complet = "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs)

    indicateurs = container.find_all("p", class_="C71Indicateur")
    indicateur_text = "\n\n".join(p.get_text(" ", strip=True) for p in indicateurs)

    dispositifs = container.find_all("p", class_=re.compile(r"Dispositif"))
    dispositif_text = "\n\n".join(p.get_text(" ", strip=True) for p in dispositifs)

    return texte_complet, dispositif_text, indicateur_text, False

def build_unique_txt_name(row: pd.Series) -> str:
    affaire = safe_filename(row.get("Affaire", ""))
    logic = safe_filename(row.get("LogicDocId", ""))
    cid = safe_filename(row.get("Id", ""))

    if affaire and logic:
        return f"{affaire}__{logic}.txt"
    if affaire and cid:
        return f"{affaire}__{cid}.txt"
    if affaire:
        return f"{affaire}.txt"
    if logic:
        return f"{logic}.txt"
    if cid:
        return f"{cid}.txt"
    return "document.txt"

def fix_infocuria_year_in_url(url: str, date_str: str | None) -> str:
    """
    Corrige l'année dans les URLs du type:
    .../blob/download-file-html/C/2099/... -> .../C/1999/...
    en prenant l'année depuis date_str (YYYY-...).
    Si date_str est vide, applique une heuristique (99 -> 1999, 05 -> 2005).
    """
    if not url:
        return url

    # 1) année depuis la date (le plus fiable)
    year = None
    if date_str and isinstance(date_str, str) and len(date_str) >= 4 and date_str[:4].isdigit():
        year = date_str[:4]

    # 2) fallback: heuristique depuis l’URL (si pas de date)
    if year is None:
        m = re.search(r"/blob/download-file-html/[A-Z]/(\d{4})/", url)
        if m:
            y = int(m.group(1))
            # Si on détecte un 20xx "absurde" (ex: 2099), on tente de corriger via les 2 derniers chiffres
            if y >= 2050:  # seuil volontairement haut
                yy = y % 100
                year = f"19{yy:02d}"
            else:
                year = str(y)

    if year is None:
        return url

    # Remplacement strict du segment /C/YYYY/ (ou /T/YYYY/, etc.)
    return re.sub(r"(/blob/download-file-html/[A-Z]/)\d{4}(/)", rf"\g<1>{year}\2", url)


def main():
    os.makedirs(csv_v1_directory, exist_ok=True)
    os.makedirs(textes_directory, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    })

    for page in range(1, MAX_PAGES + 1):
        in_path = os.path.join(csv_pdf_directory, f"corpus_page_{page}.csv")
        if not os.path.exists(in_path):
            print(f"❌ Fichier introuvable: {in_path}")
            return

        df = pd.read_csv(in_path)

        if "Lien" not in df.columns:
            raise ValueError("❌ Colonne 'Lien' absente du CSV d'entrée.")
        if "Est_pdf" not in df.columns:
            df["Est_pdf"] = "non"

        page_folder = os.path.join(textes_directory, f"page {page}")
        os.makedirs(page_folder, exist_ok=True)

        # On repart de START_AT_ROW uniquement pour la page 1 (à adapter si multi-pages)
        start = START_AT_ROW if page == 1 else 0

        print(f"\n➡️ Page {page} | reprise à la ligne index={start} (affichage {start+1}/{len(df)})")

        rows_out = []
        # Si un CSV v1 existe déjà, on le recharge pour ne pas perdre les colonnes enrichies
        out_csv = os.path.join(csv_v1_directory, f"corpus_page_{page}.csv")
        if os.path.exists(out_csv):
            df_existing = pd.read_csv(out_csv)
            # On repart de l'existant (important pour conserver les 520 déjà traités)
            rows_out = df_existing.to_dict("records")
            print(f"✅ CSV v1 existant détecté, {len(df_existing)} lignes chargées.")
        else:
            rows_out = df.to_dict("records")
            print("ℹ️ Pas de CSV v1 existant → on crée depuis l’entrée.")

        # Traitement seulement à partir de start
        for i in range(start, len(df)):
            row = df.iloc[i]
            url = str(row.get("Lien", "")).strip()
            url = fix_infocuria_year_in_url(url, row.get("Date"))

            est_pdf = str(row.get("Est_pdf", "")).strip().lower()

            # nom fichier cible
            base_nom = build_unique_txt_name(row)
            txt_path = os.path.join(page_folder, base_nom)

            print(f"\n[{i+1}/{len(df)}] {row.get('Affaire','(sans affaire)')} | url={url}")

            # Si déjà écrit, on skip
            if base_nom and os.path.exists(txt_path):
                print(f"↪️ Déjà présent, skip: {txt_path}")
                continue

            dispositif_text = ""
            indicateur_text = ""
            texte_complet = ""

            if est_pdf == "oui":
                print("↪️ PDF détecté → skip")
                continue

            if not url:
                print("⚠️ URL vide → skip")
                continue

            try:
                r = session.get(url, timeout=30)
                time.sleep(random.uniform(1.0, 2.5))

                if r.status_code != 200:
                    print(f"⚠️ HTTP {r.status_code}")
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                container = get_container(soup)
                texte_complet, dispositif_text, indicateur_text, ancien = extract_texts_from_container(container)

                if not texte_complet.strip():
                    print("⚠️ Texte vide après parsing")
                    continue

                if ancien:
                    print("ℹ️ Ancien format détecté.")

                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(texte_complet)
                print(f"✅ Texte écrit: {txt_path}")

                # Met à jour la ligne dans rows_out
                # (on suppose même ordre et même taille)
                rows_out[i]["Dispositif"] = dispositif_text
                rows_out[i]["Indicateur"] = indicateur_text
                rows_out[i]["Fichier texte"] = base_nom

            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur request: {e}")

        # Sauvegarde finale
        pd.DataFrame(rows_out).to_csv(out_csv, index=False, encoding="utf-8")
        print(f"\n✅ CSV mis à jour: {out_csv}")

if __name__ == "__main__":
    main()
