import json
import argparse
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Tracer la répartition du nombre d'arrêts par année"
)
parser.add_argument(
    "--input",
    required=True,
    help="Fichier JSON Legifrance (liste de documents)"
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
# COMPTAGE PAR ANNÉE
# ======================================================
count_by_year = defaultdict(int)

for doc in data:
    try:
        ts = doc["text"]["dateTexte"]
    except (KeyError, TypeError):
        continue

    if not isinstance(ts, (int, float)):
        continue

    try:
        year = datetime.fromtimestamp(ts / 1000).year
        count_by_year[year] += 1
    except Exception:
        continue

if not count_by_year:
    raise ValueError("❌ Aucune date exploitable trouvée")

# ======================================================
# PRÉPARATION DES DONNÉES
# ======================================================
years = sorted(count_by_year.keys())
counts = [count_by_year[y] for y in years]

# ======================================================
# PLOT
# ======================================================
plt.figure(figsize=(12, 6))

plt.bar(years, counts, color="#70e1e6")

plt.xlabel("Année")
plt.ylabel("Nombre d'arrêts")
plt.title("Les arrêts de la chambre criminelle citant des sources émanant du Conseil de l'Europe")

# 👉 forcer l'affichage de TOUTES les années
plt.xticks(years, rotation=45)

plt.tight_layout()
plt.show()

