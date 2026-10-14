import json
import argparse
import re

# ======================================================
# ARGUMENTS CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Filtrage case-sensitive des arrêts via mots-clés (.txt) avec export des exclus"
)

parser.add_argument("--input", required=True, help="JSON des arrêts complets")
parser.add_argument("--keywords", required=True, help="Fichier txt de mots-clés")
parser.add_argument("--output-kept", required=True, help="JSON des arrêts retenus")
parser.add_argument("--output-excluded", required=True, help="JSON des arrêts exclus")

args = parser.parse_args()

# ======================================================
# CHARGEMENT DES MOTS-CLÉS
# ======================================================
with open(args.keywords, "r", encoding="utf-8") as f:
    keywords = [line.strip() for line in f if line.strip()]

print(f"🔎 {len(keywords)} mots-clés chargés")

# ======================================================
# COMPILATION DES REGEX (CASE-SENSITIVE)
# ======================================================
patterns = []

for kw in keywords:
    # sigles courts : frontières de mots
    if kw.isupper() and len(kw) <= 6:
        patterns.append(re.compile(rf"\b{re.escape(kw)}\b"))
    else:
        patterns.append(re.compile(re.escape(kw)))

# ======================================================
# CHARGEMENT DU CORPUS
# ======================================================
with open(args.input, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise ValueError("❌ Le fichier input doit contenir une liste")

# ======================================================
# FILTRAGE
# ======================================================
kept = []
excluded = []

for doc in data:
    text_obj = doc.get("text", {})
    texte = text_obj.get("texte", "")
    titre = text_obj.get("titre", "")
    titre_long = text_obj.get("titreLong", "")

    corpus = f"{titre}\n{titre_long}\n{texte}"

    if any(p.search(corpus) for p in patterns):
        kept.append(doc)
    else:
        excluded.append(doc)

# ======================================================
# SAUVEGARDE
# ======================================================
with open(args.output_kept, "w", encoding="utf-8") as f:
    json.dump(kept, f, ensure_ascii=False, indent=2)

with open(args.output_excluded, "w", encoding="utf-8") as f:
    json.dump(excluded, f, ensure_ascii=False, indent=2)

print("✅ Filtrage terminé")
print(f"➡️ Arrêts retenus : {len(kept)}")
print(f"➡️ Arrêts exclus  : {len(excluded)}")
print(f"📁 Retenus  : {args.output_kept}")
print(f"📁 Exclus   : {args.output_excluded}")
