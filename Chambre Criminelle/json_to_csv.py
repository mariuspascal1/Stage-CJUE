import json
import csv
import argparse
import os
from datetime import datetime, timezone

# ======================================================
# CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Extraction métadonnées JSON Legifrance vers CSV + textes en TXT"
)
parser.add_argument("--input", required=True, help="Fichier JSON (arrêts complets)")
parser.add_argument("--output", required=True, help="Fichier CSV de sortie")
parser.add_argument(
    "--date-field",
    default="dateTexte",
    help="Champ de date à utiliser (par défaut: dateTexte)"
)
parser.add_argument(
    "--text-dir",
    default="Textes",
    help="Dossier de sortie des fichiers .txt"
)
args = parser.parse_args()

# ======================================================
# HELPERS
# ======================================================
def ms_to_iso_date(ms):
    if not isinstance(ms, (int, float)):
        return ""
    try:
        dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""

def join_numero_affaire(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(x) for x in value if x is not None)
    return str(value)

def clean(s):
    return "" if s is None else str(s)

# ======================================================
# LOAD JSON
# ======================================================
with open(args.input, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise ValueError("❌ Le JSON doit être une liste")

# ======================================================
# PREP TXT DIR
# ======================================================
os.makedirs(args.text_dir, exist_ok=True)

# ======================================================
# WRITE CSV + TXT
# ======================================================
fieldnames = ["id", "numeroAffaire", "date", "titre", "citationJp"]

with open(args.output, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for doc in data:
        text = doc.get("text", {}) if isinstance(doc, dict) else {}

        arret_id = clean(text.get("id"))
        texte_complet = clean(text.get("texte"))

        # ---------- CSV ----------
        writer.writerow({
            "id": arret_id,
            "numeroAffaire": join_numero_affaire(text.get("numeroAffaire")),
            "date": ms_to_iso_date(text.get(args.date_field)),
            "titre": clean(text.get("titre")),
            "citationJp": clean(text.get("citationJp")),
        })

        # ---------- TXT ----------
        if arret_id and texte_complet:
            with open(
                os.path.join(args.text_dir, f"{arret_id}.txt"),
                "w",
                encoding="utf-8"
            ) as out:
                out.write(texte_complet)

print("✅ Extraction terminée")
print(f"📄 CSV : {args.output}")
print(f"📚 Textes : {args.text_dir}/")
