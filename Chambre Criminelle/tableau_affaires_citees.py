import argparse
import csv
import re
import sys

# ======================================================
# CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Tableau des seules affaires CJUE citées par la chambre criminelle, avec indicateur présence dans le corpus CJUE"
)
parser.add_argument("--crim", required=True, help="CSV chambre criminelle (avec reference_a)")
parser.add_argument("--cjue", required=True, help="CSV corpus CJUE (avec Numéro d’affaire)")
parser.add_argument("--output", required=True, help="CSV de sortie (affaires citées uniquement)")

parser.add_argument("--crim_ref_col", default="reference_a", help="Colonne refs CJUE dans CRIM")
parser.add_argument("--crim_numaff_col", default="numeroAffaire", help="Colonne numeroAffaire crim")

parser.add_argument("--cjue_case_col", default="Numéro d’affaire", help="Colonne affaire CJUE dans corpus")
parser.add_argument("--cjue_penal_col", default="Relatif au pénal", help="Colonne pénal dans corpus")
args = parser.parse_args()

# ======================================================
# Lever la limite de taille des champs CSV
# ======================================================
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(10_000_000)

# ======================================================
# Normalisation des références CJUE
# - accepte : C-150/88, C- 267/91, C - 267 / 91, tirets unicode, etc.
# - sort toujours : C-267/91
# ======================================================
DASH_CHARS = r"\-\u2010\u2011\u2012\u2013\u2014"
CASE_RE = re.compile(rf"\bC\s*[{DASH_CHARS}]\s*(\d+)\s*/\s*(\d+)\b")

def norm_case(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    m = CASE_RE.search(s)
    if m:
        return f"C-{m.group(1)}/{m.group(2)}"
    # si ça ne matche pas, on tente une normalisation légère quand même
    s = re.sub(rf"[{DASH_CHARS}]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def split_refs(refs: str):
    if not refs:
        return []
    parts = [p.strip() for p in refs.split(";")]
    out = []
    for p in parts:
        p2 = norm_case(p)
        if p2:
            out.append(p2)
    return out

# ======================================================
# 1) Lire le corpus CJUE -> set d'affaires + pénal
# ======================================================
cjue_cases = set()
cjue_penal = {}

with open(args.cjue, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        raise ValueError("❌ CSV CJUE sans en-têtes")

    for col in (args.cjue_case_col,):
        if col not in reader.fieldnames:
            raise ValueError(f"❌ Colonne '{col}' introuvable dans CJUE. Dispo: {reader.fieldnames}")

    # penal col optionnelle (si elle n'existe pas, on mettra vide)
    penal_exists = args.cjue_penal_col in reader.fieldnames

    for row in reader:
        case_raw = (row.get(args.cjue_case_col) or "").strip()
        case = norm_case(case_raw)
        if not case:
            continue
        cjue_cases.add(case)
        if penal_exists:
            cjue_penal[case] = (row.get(args.cjue_penal_col) or "").strip()

# ======================================================
# 2) Lire le CSV crim -> dictionnaire case -> set(nums crim)
# ======================================================
cited_by = {}  # case -> set(numeroAffaire crim)

with open(args.crim, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        raise ValueError("❌ CSV crim sans en-têtes")

    for col in (args.crim_ref_col, args.crim_numaff_col):
        if col not in reader.fieldnames:
            raise ValueError(f"❌ Colonne '{col}' introuvable dans CRIM. Dispo: {reader.fieldnames}")

    for row in reader:
        crim_num = (row.get(args.crim_numaff_col) or "").strip()
        refs = split_refs(row.get(args.crim_ref_col, ""))

        for case in refs:
            cited_by.setdefault(case, set()).add(crim_num)

# ======================================================
# 3) Écrire le CSV "affaires citées uniquement"
# ======================================================
out_fields = [
    "Numéro d'affaire",
    "Présent dans le corpus CJUE",
    "Relatif au pénal",
    "numeroAffaire (chambre criminelle)",
]

with open(args.output, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=out_fields)
    writer.writeheader()

    for case in sorted(cited_by.keys()):
        crim_nums = sorted([x for x in cited_by.get(case, set()) if x])
        in_corpus = "oui" if case in cjue_cases else "non"

        writer.writerow({
            "Numéro d'affaire": case,
            "Présent dans le corpus CJUE": in_corpus,
            "Relatif au pénal": cjue_penal.get(case, ""),
            "numeroAffaire (chambre criminelle)": "; ".join(crim_nums),
        })

print("✅ Terminé")
print(f"➡️ Affaires CJUE citées : {len(cited_by)}")
print(f"📁 CSV généré : {args.output}")
