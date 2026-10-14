import requests
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

# ======================================================
# ARGUMENTS CLI (optionnel)
# ======================================================
parser = argparse.ArgumentParser(description="Test proximité directive / CE")
parser.add_argument("--distance", type=int, default=4, help="Distance de proximité")
parser.add_argument("--formation", default="CHAMBRE_CRIMINELLE")
parser.add_argument("--fond", default="JURI")
args = parser.parse_args()

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

print("🔐 Obtention du token...")
token_response = requests.post(token_url, data=auth_data)
token_response.raise_for_status()
access_token = token_response.json()["access_token"]
print("✅ Token obtenu")

# ======================================================
# REQUÊTE API (PROXIMITÉ)
# ======================================================
url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/search"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

payload = {
    "fond": args.fond,
    "recherche": {
        "champs": [
            {
                "typeChamp": "ALL",
                "operateur": "ET",
                "criteres": [
                    {
                    "valeur": "directive CE",
                    "proximite": 3,
                    "typeRecherche": "TOUS_LES_MOTS"
                    }

                ],
            }
        ],
        "filtres": [
            {
                "facette": "CASSATION_FORMATION",
                "valeurs": [args.formation],
            }
        ],
        "operateur": "ET",
        "pageSize": 1,              # 👈 UNE SEULE ENTRÉE SUFFIT
        "typePagination": "DEFAUT",
        "pageNumber": 1,
    },
}

print("\n📡 Lancement de la requête test...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print("❌ Erreur HTTP", response.status_code)
    print(response.text)
    exit(1)

data = response.json()
total = data.get("totalResultNumber", 0)

print("\n📊 RÉSULTAT DU TEST")
print(f"➡️ directive NEAR/{args.distance} CE")
print(f"➡️ Nombre de documents trouvés : {total}")
