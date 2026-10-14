import json
import argparse
import re
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Tracer la répartition du nombre d'arrêts par année (titre prioritaire)"
)
parser.add_argument(
    "--input",
    required=True,
    help="Fichier JSON Legifrance (arrêts complets)"
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
# OUTILS DATE
# ======================================================
mois_fr = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}

regex_date_titre = re.compile(
    r"du\s+(\d{1,2})\s+"
    r"(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|"
    r"septembre|octobre|novembre|décembre|decembre)\s+"
    r"(\d{4})",
    re.IGNORECASE
)

def extract_year(doc):
    """Extrait l'année depuis le titre, sinon depuis dateTexte"""
    text = doc.get("text", {})

    # 1️⃣ TITRE (source fiable)
    titre = text.get("titre") or text.get("titreLong")
    if isinstance(titre, str):
        match = regex_date_titre.search(titre.lower())
        if match:
            day = int(match.group(1))
            month = mois_fr[match.group(2)]
            year = int(match.group(3))
            try:
                return datetime(year, month, day).year
            except ValueError:
                pass

    # 2️⃣ FALLBACK : timestamp dateTexte
    ts = text.get("dateTexte")
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(ts / 1000).year
        except Exception:
            pass

    return None

# ======================================================
# COMPTAGE PAR ANNÉE
# ======================================================
count_by_year = defaultdict(int)
ignored = 0

for doc in data:
    year = extract_year(doc)
    if year:
        count_by_year[year] += 1
    else:
        ignored += 1

if not count_by_year:
    raise ValueError("❌ Aucune date exploitable trouvée")

print(f"📊 Arrêts exploitables : {sum(count_by_year.values())}")
print(f"⚠️ Arrêts ignorés (date absente/invalide) : {ignored}")

# ======================================================
# DONNÉES POUR LE PLOT
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
plt.title("Répartition du nombre d'arrêts rendus par année")

# 👉 afficher toutes les années
plt.xticks(years, rotation=45)

plt.tight_layout()
plt.show()
