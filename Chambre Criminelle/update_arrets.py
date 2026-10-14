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
    description="Mise à jour des arrêts complets Legifrance (avec reprise depuis backup)"
)

parser.add_argument("--input", required=True, help="Fichier JSON des nouveaux arrêts")
parser.add_argument("--output", required=True, help="Fichier JSON existant des arrêts complets")
parser.add_argument("--resume-from", type=int, default=None, help="Index de reprise manuel")
parser.add_argument("--backup-every", type=int, default=200)
parser.add_argument("--pause-every", type=int, default=100)
parser.add_argument("--pause-duration", type=int, default=10)
parser.add_argument("--small-pause", type=float, default=0.3)

args = parser.parse_args()

# ======================================================
# AUTHENTIFICATION
# ======================================================
def get_token():
    token_url = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": os.environ["PISTE_CLIENT_ID"],
        "client_secret": os.environ["PISTE_CLIENT_SECRET"],
        "scope": "openid"
    }
    print("🔐 Obtention d’un nouveau token...")
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    print("✅ Token obtenu")
    return response.json()["access_token"]

def fetch_arret(identifiant, token):
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/juri"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {"textId": identifiant}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 401:
        print("⚠️ Token expiré — renouvellement...")
        new_token = get_token()
        headers["Authorization"] = f"Bearer {new_token}"
        response = requests.post(url, headers=headers, json=payload)
        return response, new_token

    return response, token

# ======================================================
# INITIALISATION
# ======================================================
access_token = get_token()

# ======================================================
# CHARGEMENT DES NOUVEAUX IDS
# ======================================================
with open(args.input, "r", encoding="utf-8") as f:
    data_new = json.load(f)

if isinstance(data_new, dict) and "results" in data_new:
    nouveaux_arrets = data_new["results"]
elif isinstance(data_new, list):
    nouveaux_arrets = data_new
else:
    raise ValueError("❌ Format du JSON input inattendu")

print(f"📄 {len(nouveaux_arrets)} nouveaux arrêts trouvés")

# ======================================================
# CHARGEMENT DES ARRÊTS EXISTANTS
# ======================================================
if not os.path.exists(args.output):
    raise FileNotFoundError("❌ Le fichier output n'existe pas")

with open(args.output, "r", encoding="utf-8") as f:
    resultats_complets = json.load(f)

print(f"📦 {len(resultats_complets)} arrêts déjà présents")

# --- index robuste des identifiants existants
ids_existants = set()
for doc in resultats_complets:
    if not isinstance(doc, dict):
        continue
    ident = doc.get("identifiant") or doc.get("text", {}).get("id")
    if ident:
        ids_existants.add(ident)

# ======================================================
# FILTRAGE DES NOUVEAUX IDS
# ======================================================
a_telecharger = []

for arret in nouveaux_arrets:
    if isinstance(arret.get("titles"), list) and arret["titles"]:
        identifiant = arret["titles"][0].get("id") or arret["titles"][0].get("cid")
        if identifiant and identifiant not in ids_existants:
            a_telecharger.append(identifiant)

print(f"⬇️ {len(a_telecharger)} nouveaux arrêts à télécharger")

# ======================================================
# REPRISE (backup / auto)
# ======================================================
last_backup_file = None

if args.resume_from is not None:
    backup_file = args.output.replace(".json", f"_backup_update_{args.resume_from}.json")
    if os.path.exists(backup_file):
        print(f"🔄 Reprise depuis backup {backup_file}")
        with open(backup_file, "r", encoding="utf-8") as f:
            resultats_complets = json.load(f)
        last_backup_file = backup_file
    start_index = args.resume_from
    print(f"▶️ Reprise manuelle à l’index {start_index}")
else:
    start_index = 0
    print("▶️ Démarrage normal")

# ======================================================
# TÉLÉCHARGEMENT
# ======================================================
total = len(a_telecharger)

for i, identifiant in enumerate(a_telecharger[start_index:], start=start_index + 1):
    print(f"[{i}/{total}] 📥 {identifiant}")

    try:
        response, access_token = fetch_arret(identifiant, access_token)
    except requests.RequestException as e:
        print(f"❌ Erreur réseau : {e}")
        time.sleep(5)
        continue

    if response.status_code != 200:
        print(f"❌ Erreur HTTP {response.status_code}")
        continue

    try:
        texte_complet = response.json()
        texte_complet["identifiant"] = identifiant
        resultats_complets.append(texte_complet)
        ids_existants.add(identifiant)
    except Exception as e:
        print(f"❌ Erreur JSON : {e}")
        continue

    # ---------------- BACKUP UNIQUE ----------------
    if i % args.backup_every == 0:
        backup_file = args.output.replace(".json", f"_backup_update_{i}.json")

        if last_backup_file and os.path.exists(last_backup_file):
            os.remove(last_backup_file)
            print(f"🗑 Suppression backup : {last_backup_file}")

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(resultats_complets, f, ensure_ascii=False, indent=2)

        print(f"💾 Backup créé : {backup_file}")
        last_backup_file = backup_file

    if i % args.pause_every == 0:
        print(f"⏸ Pause longue ({args.pause_duration}s)")
        time.sleep(args.pause_duration)

    time.sleep(args.small_pause)

# ======================================================
# SAUVEGARDE FINALE
# ======================================================
if last_backup_file and os.path.exists(last_backup_file):
    os.remove(last_backup_file)
    print(f"🗑 Backup final supprimé : {last_backup_file}")

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(resultats_complets, f, ensure_ascii=False, indent=2)

print("\n✅ MISE À JOUR TERMINÉE")
print(f"➡️ Total arrêts : {len(resultats_complets)}")
print(f"📁 Fichier final : {args.output}")
