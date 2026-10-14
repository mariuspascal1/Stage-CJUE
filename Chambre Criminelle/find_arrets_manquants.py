import json
import argparse
import os

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Identifier les arrêts présents dans *_total.json mais absents de *_complets.json"
)
parser.add_argument("--total", required=True, help="Fichier JSON des arrêts (total)")
parser.add_argument("--complets", required=True, help="Fichier JSON des arrêts complets")
parser.add_argument("--output", required=True, help="Fichier JSON de sortie (arrêts manquants)")
args = parser.parse_args()

# ======================================================
# CHARGEMENT DES FICHIERS
# ======================================================
with open(args.total, "r", encoding="utf-8") as f:
    data_total = json.load(f)

with open(args.complets, "r", encoding="utf-8") as f:
    data_complets = json.load(f)

if not isinstance(data_total, list):
    raise ValueError("❌ Le fichier TOTAL doit contenir une liste")

if not isinstance(data_complets, list):
    raise ValueError("❌ Le fichier COMPLETS doit contenir une liste")

# ======================================================
# EXTRACTION DES IDENTIFIANTS COMPLETS
# ======================================================
ids_complets = set()

for doc in data_complets:
    # priorité : identifiant ajouté par ton script
    ident = doc.get("identifiant")

    # fallback : text.id
    if not ident:
        ident = doc.get("text", {}).get("id")

    if ident:
        ids_complets.add(ident)

print(f"✅ Identifiants complets : {len(ids_complets)}")

# ======================================================
# FILTRAGE DES MANQUANTS
# ======================================================
manquants = []

for doc in data_total:
    ident = None

    if isinstance(doc.get("titles"), list) and doc["titles"]:
        ident = doc["titles"][0].get("id") or doc["titles"][0].get("cid")

    if not ident:
        continue

    if ident not in ids_complets:
        manquants.append(doc)

# ======================================================
# SAUVEGARDE
# ======================================================
with open(args.output, "w", encoding="utf-8") as f:
    json.dump(manquants, f, ensure_ascii=False, indent=2)

# ======================================================
# RÉCAP
# ======================================================
print("\n📊 RÉCAPITULATIF")
print(f"➡️ Arrêts total      : {len(data_total)}")
print(f"➡️ Arrêts complets   : {len(ids_complets)}")
print(f"❌ Arrêts manquants  : {len(manquants)}")
print(f"📁 Fichier généré   : {args.output}")
