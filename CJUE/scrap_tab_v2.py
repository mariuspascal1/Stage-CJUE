import time
import re
import requests
import pandas as pd

SEARCH_URL = "https://infocuriaws.curia.europa.eu/elastic-connector/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

BASE_PAYLOAD = {
    "searchTerm": "pénal, pénale, pénales",
    "multiSearchTerms": [],
    "sortTermList": [{"sortDirection": "DESC", "sortTerm": "DOC_DATE", "sortSourceTab": "jurisprudence"}],
    "pagination": {"pageNumber": 0, "pageSize": 20, "from": 1, "to": 20},
    "language": "FR",
    "tabName": "jurisprudence",
    "isAllTabsRequest": False,
    "ecli": "",
    "publishedId": "",
    "usualName": "",
    "logicDocId": "",
    "filtersValue": [
        {"field": "affairJurisdiction", "values": ["C"], "valuesWithFullHierarchy": ["C"]},
        {"field": "docType", "values": ["ARRET"], "valuesWithFullHierarchy": ["ARRET"]},
        {"field": "docDate", "values": ["1800-01-01", "2025-12-31"], "valuesWithFullHierarchy": ["1800-01-01", "2025-12-31"]},
    ],
    "isSearchExact": True,
    "searchSources": ["document", "metadata"],
}

def fetch_page(page_number: int, page_size: int = 50) -> dict:
    payload = dict(BASE_PAYLOAD)
    payload["pagination"] = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "from": page_number * page_size + 1,
        "to": (page_number + 1) * page_size,
    }
    r = requests.post(SEARCH_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def build_html_url(case_id: str | None, logic_doc_id: str | None) -> str | None:
    """
    Construit:
    https://infocuriaws.curia.europa.eu/blob/download-file-html/C/2024/C_0366_24_00000000RP_01_P_01/313764-FR-1.html
    à partir de:
      - case_id:      "C/0366/24/00000000RP/01/P/01-3390385"
      - logic_doc_id: "id_313764"
    """
    if not case_id or not logic_doc_id:
        return None

    # Juridiction + année (de l'affaire)
    m = re.match(r"^(?P<jur>[A-Z])/(?P<num>\d{1,4})/(?P<yy>\d{2})/", case_id)
    if not m:
        return None
    jur = m.group("jur")                    # "C"
    num = m.group("num").zfill(4)           # "0366"
    yy = m.group("yy")                      # "24"
    yyyy = "20" + yy                        # "2024"

    # Base de l'id sans le suffixe "-xxxxxxx"
    base = case_id.split("-", 1)[0]         # "C/0366/24/00000000RP/01/P/01"
    base_undersc = base.replace("/", "_")   # "C_0366_24_00000000RP_01_P_01"

    # logicDocId => chiffres uniquement
    logic_num = re.sub(r"\D", "", logic_doc_id)  # "313764"
    if not logic_num:
        return None

    return (
        f"https://infocuriaws.curia.europa.eu/blob/download-file-html/"
        f"{jur}/{yyyy}/{base_undersc}/{logic_num}-FR-1.html"
    )

def extract_rows(resp: dict) -> list[dict]:
    hits = resp.get("searchHits", []) or []
    rows = []
    for h in hits:
        c = h.get("content", {}) or {}

        affaire = c.get("idPublished")       # ex: C-366/24
        date = c.get("docDate")              # ex: 2025-12-18
        doc_type = c.get("docType")          # ex: Arrêt
        type_code = c.get("docTypeCode")     # ex: ARRET
        ecli = c.get("ecli")
        nom_usuel = c.get("usualName") or c.get("celeTitle") or c.get("title")
        logic_doc_id = c.get("logicDocId")   # ex: id_313764
        case_id = c.get("id")                # ex: C/0366/24/....-xxxx
        formats = ";".join(c.get("docFormats", []) or [])

        lien_html_fr = build_html_url(case_id, logic_doc_id)

        rows.append({
            "Numéro d'affaire": affaire,
            "Date": date,
            "Type": doc_type,
            "TypeCode": type_code,
            "ECLI": ecli,
            "Nom_usuel": nom_usuel,
            "LogicDocId": logic_doc_id,
            "Id": case_id,
            "Formats": formats,
            "Lien": lien_html_fr,
        })
    return rows

def scrape_all(page_size: int = 50, sleep_s: float = 0.2) -> pd.DataFrame:
    first = fetch_page(0, page_size=page_size)
    total = int(first.get("totalHits", 0) or 0)

    all_rows = extract_rows(first)

    total_pages = (total + page_size - 1) // page_size

    for p in range(1, total_pages):
        time.sleep(sleep_s)
        resp = fetch_page(p, page_size=page_size)
        all_rows.extend(extract_rows(resp))

    return pd.DataFrame(all_rows)

if __name__ == "__main__":
    df = scrape_all(page_size=50)
    print(df.head(10))
    df.to_csv("/Users/mariuspascal/Desktop/CJUE/corpus_update/infoCuria/corpus_infocuria_api.csv", index=False, encoding="utf-8")
    print(f"OK: {len(df)} résultats exportés.")
