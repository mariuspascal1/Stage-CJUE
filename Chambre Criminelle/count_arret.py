import json
import argparse
import os

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Compter le nombre d'arrêts dans un fichier JSON Legifrance"
)
parser.add_argument(
    "--file",
    required=True,
    help="Chemin vers le fichier JSON"
)

args = parser.parse_args()

# ======================================================
# CHARGEMENT DU FICHIER
# ======================================================
if not os.path.exists(args.file):
    raise FileNotFoundError(f"❌ Fichier introuvable : {args.file}")

with open(args.file, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise ValueError("❌ Le fichier JSON n'est pas une liste de documents")

# ======================================================
# COMPTAGE DES ARRÊTS
# ======================================================
total_documents = len(data)

arrets = [
    doc for doc in data
    if isinstance(doc, dict) and doc.get("nature") == "arret"
]

total_arrets = len(arrets)

# ======================================================
# AFFICHAGE
# ======================================================
print("📊 RÉSULTAT")
print(f"➡️ Nombre total de documents : {total_documents}")
print(f"➡️ Nombre d'arrêts            : {total_arrets}")
