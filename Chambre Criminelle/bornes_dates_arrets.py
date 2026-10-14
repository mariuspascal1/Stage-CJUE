import json
import argparse
from datetime import datetime

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Affiche la date du premier et du dernier arrêt d'un fichier JSON Legifrance"
)
parser.add_argument(
    "--input",
    required=True,
    help="Fichier JSON des arrêts complets"
)
args = parser.parse_args()

# ======================================================
# CHARGEMENT DU JSON
# ======================================================
with open(args.input, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise ValueError("❌ Le JSON doit contenir une liste")

# ======================================================
# EXTRACTION DES DATES
# ======================================================
dates = []

for doc in data:
    try:
        ts = doc["text"]["dateTexte"]
        if isinstance(ts, (int, float)):
            date = datetime.fromtimestamp(ts / 1000)
            dates.append(date)
    except (KeyError, TypeError):
        continue

if not dates:
    raise ValueError("❌ Aucune date exploitable trouvée")

# ======================================================
# RÉSULTATS
# ======================================================
date_min = min(dates)
date_max = max(dates)

print("📅 Bornes temporelles des arrêts :\n")
print(f"🥇 Premier arrêt : {date_min.strftime('%d/%m/%Y')}")
print(f"🏁 Dernier arrêt  : {date_max.strftime('%d/%m/%Y')}")
print(f"📊 Nombre d'arrêts analysés : {len(dates)}")
