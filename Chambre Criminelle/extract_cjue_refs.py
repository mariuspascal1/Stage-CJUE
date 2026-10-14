import argparse
import csv
import os
import re

# ======================================================
# CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Extraction des références CJUE (format C-150/88) depuis des fichiers .txt (un par arrêt)"
)
parser.add_argument("--input", required=True, help="CSV d'entrée (métadonnées, doit contenir une colonne id)")
parser.add_argument("--output", required=True, help="CSV de sortie enrichi")
parser.add_argument("--text-dir", default="Textes", help="Dossier contenant les fichiers .txt (défaut: Textes)")
parser.add_argument("--id-col", default="id", help="Nom de la colonne contenant l'id (défaut: id)")
parser.add_argument("--out-col", default="reference_a", help="Nom de la colonne de sortie (défaut: reference_a)")
parser.add_argument("--missing-col", default="texte_manquant", help="Colonne booléenne si .txt absent (défaut: texte_manquant)")
args = parser.parse_args()

# ======================================================
# REGEX
# - accepte: C-150/88, C- 267/91, C - 267 / 91, etc.
# - gère les tirets unicode (hyphen, non-breaking hyphen, en dash…)
# ======================================================

DASH_CHARS = r"-\u2010\u2011\u2012\u2013\u2014"  # - ‐ - ‒ – —
pattern = re.compile(
    rf"\bC\s*[{DASH_CHARS}]\s*(\d+)\s*/\s*(\d+)\s*(PPU|P)?\b",
    flags=re.IGNORECASE
)


def extract_cases(text: str) -> str:
    """Retourne 'C-150/88; C-267/91; C-10/18 P; C-107/23 PPU' (unique, normalisé)."""
    if not text:
        return ""

    matches = []
    for m in pattern.finditer(text):
        num1, num2 = m.group(1), m.group(2)
        suffix = m.group(3)  # None, 'P', 'PPU'
        if suffix:
            matches.append(f"C-{num1}/{num2} {suffix.upper()}")
        else:
            matches.append(f"C-{num1}/{num2}")

    seen = set()
    unique = []
    for x in matches:
        if x not in seen:
            seen.add(x)
            unique.append(x)

    return "; ".join(unique)


def read_txt_for_id(text_dir: str, arret_id: str) -> str:
    """Lit Textes/<id>.txt. Retourne '' si absent."""
    if not arret_id:
        return ""
    path = os.path.join(text_dir, f"{arret_id}.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ======================================================
# CSV -> CSV enrichi (lecture des .txt)
# ======================================================
with open(args.input, "r", encoding="utf-8", newline="") as f_in:
    reader = csv.DictReader(f_in)
    fieldnames = list(reader.fieldnames) if reader.fieldnames else []

    if args.id_col not in fieldnames:
        raise ValueError(f"❌ Colonne '{args.id_col}' introuvable. Colonnes dispo: {fieldnames}")

    # Ajoute colonnes si absentes
    if args.out_col not in fieldnames:
        fieldnames.append(args.out_col)
    if args.missing_col not in fieldnames:
        fieldnames.append(args.missing_col)

    with open(args.output, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        n = 0
        n_missing = 0

        for row in reader:
            arret_id = (row.get(args.id_col) or "").strip()
            txt = read_txt_for_id(args.text_dir, arret_id)

            if not txt:
                row[args.out_col] = ""
                row[args.missing_col] = "1"
                n_missing += 1
            else:
                row[args.out_col] = extract_cases(txt)
                row[args.missing_col] = "0"

            writer.writerow(row)
            n += 1

print("✅ Terminé")
print(f"➡️ Lignes traitées : {n}")
print(f"⚠️ Textes manquants : {n_missing}")
print(f"📁 CSV généré : {args.output}")
