import requests
import json
import time
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Recherche Legifrance avec mots-clés externes (découpage par année)"
)
parser.add_argument("--keywords", required=True, help="Fichier txt de mots-clés")
parser.add_argument("--output", required=True, help="Dossier de sortie")
parser.add_argument("--basename", required=True, help="Nom de base des fichiers JSON")
parser.add_argument("--formation", default="CHAMBRE_CRIMINELLE")
parser.add_argument("--fond", default="JURI")
parser.add_argument("--page-size", type=int, default=100)
parser.add_argument("--start-year", type=int, default=1900)
parser.add_argument("--end-year", type=int, default=2026)
args = parser.parse_args()

# ======================================================
# CHARGEMENT DES MOTS-CLÉS
# ======================================================
with open(args.keywords, "r", encoding="utf-8") as f:
    mots_cles = [line.strip() for line in f if line.strip()]

if not mots_cles:
    raise ValueError("❌ Aucun mot-clé trouvé")

print(f"🔎 {len(mots_cles)} mots-clés chargés")

os.makedirs(args.output, exist_ok=True)

# ======================================================
# AUTHENTIFICATION
# ======================================================
token_url = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
auth_data = {
    "grant_type": "client_credentials",
    "client_id": os.environ["PISTE_CLIENT_ID"],
    "client_secret": os.environ["PISTE_CLIENT_SECRET"],
    "scope": "openid",
}

print("🔐 Token…")
access_token = requests.post(token_url, data=auth_data).json()["access_token"]
print("✅ OK")

# ======================================================
# API
# ======================================================
url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/search"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ======================================================
# BOUCLE PAR ANNÉE
# ======================================================
all_results = []

for year in range(args.start_year, args.end_year + 1):
    print(f"\n==============================")
    print(f"📅 ANNÉE {year}")
    print(f"==============================")

    page = 1
    total_results_year = None
    total_affiche = False

    while True:
        print(f"📡 Page {page}")

        payload = {
            "fond": args.fond,
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "ALL",
                        "operateur": "OU",
                        "criteres": [
                            {
                                "operateur": "OU",
                                "typeRecherche": "EXACTE",
                                "valeur": mot,
                            }
                            for mot in mots_cles
                        ],
                    }
                ],
                "filtres": [
                    {
                        "facette": "CASSATION_FORMATION",
                        "valeurs": [args.formation],
                    },
                    {
                        "facette": "DATE_DECISION",
                        "dates": {
                            "start": f"{year}-01-01",
                            "end": f"{year}-12-31",
                        },
                    },
                ],
                "operateur": "ET",
                "sort": "PERTINENCE",
                "pageSize": args.page_size,
                "typePagination": "DEFAUT",
                "pageNumber": page,
            },
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"⚠️ Erreur HTTP {response.status_code}")
            print(response.text)
            break

        data = response.json()
        results = data.get("results", [])
        total_results_year = data.get("totalResultNumber", total_results_year)

        if not total_affiche and total_results_year is not None:
            pages = (total_results_year + args.page_size - 1) // args.page_size
            print(f"📊 Total {year} : {total_results_year} ({pages} pages)")
            total_affiche = True

        filename = f"{args.basename}_{year}_page{page}.json"
        with open(os.path.join(args.output, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        all_results.extend(results)

        if len(results) < args.page_size:
            print(f"✅ Fin {year}")
            break

        page += 1
        time.sleep(1.5)

# ======================================================
# FUSION FINALE
# ======================================================
final_filename = f"{args.basename}_total.json"
with open(os.path.join(args.output, final_filename), "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("\n📊 TERMINÉ")
print(f"➡️ Total collecté : {len(all_results)}")
print(f"✅ Fichier final : {final_filename}")
