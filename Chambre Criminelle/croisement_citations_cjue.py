import argparse
import csv
import sys

# ======================================================
# CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Croisement citations CJUE (chambre criminelle) vs corpus CJUE"
)
parser.add_argument("--crim", required=True, help="CSV chambre criminelle (avec reference_a)")
parser.add_argument("--cjue", required=True, help="CSV corpus CJUE (avec Numéro d’affaire)")
parser.add_argument("--output", required=True, help="CSV de sortie")

# Colonnes (avec valeurs par défaut adaptées à tes fichiers)
parser.add_argument("--crim_ref_col", default="reference_a", help="Colonne des références CJUE (défaut: reference_a)")
parser.add_argument("--crim_numaff_col", default="numeroAffaire", help="Colonne numéroAffaire crim (défaut: numeroAffaire)")

parser.add_argument("--cjue_case_col", default="Numéro d’affaire", help="Colonne affaire CJUE (défaut: Numéro d’affaire)")
parser.add_argument("--cjue_penal_col", default="Relatif au pénal", help="Colonne pénal (défaut: Relatif au pénal)")
args = parser.parse_args()

# ======================================================
# IMPORTANT : lever la limite de taille des champs CSV
# ======================================================
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    # certains environnements n’acceptent pas sys.maxsize directement
    csv.field_size_limit(10_000_000)  # 10 MB par champ, ajuste si besoin

# ======================================================
# HELPERS
# ======================================================
def split_refs(refs: str):
    """reference_a est du type 'C-150/88; C-267/91'. Retourne une liste clean."""
    if not refs:
        return []
    parts = [p.strip() for p in refs.split(";")]
    return [p for p in parts if p]

def norm_case(s: str) -> str:
    """Normalisation minimale pour matcher entre fichiers."""
    return (s or "").strip()

# ======================================================
# 1) Charger les citations depuis le CSV chambre criminelle
#    -> cited_by["C-150/88"] = {"94-85.933", "..." }
# ======================================================
cited_by = {}  # case -> set(numeroAffaire_crim)

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

        if not refs:
            continue

        for r in refs:
            r = norm_case(r)
            if not r:
                continue
            cited_by.setdefault(r, set()).add(crim_num if crim_num else "")

# ======================================================
# 2) Charger le corpus CJUE : case -> relatif_au_penal
# ======================================================
cjue_penal = {}  # case -> "oui/non/..."
cjue_cases_in_corpus = set()

with open(args.cjue, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        raise ValueError("❌ CSV CJUE sans en-têtes")

    for col in (args.cjue_case_col, args.cjue_penal_col):
        if col not in reader.fieldnames:
            raise ValueError(f"❌ Colonne '{col}' introuvable dans CJUE. Dispo: {reader.fieldnames}")

    for row in reader:
        case = norm_case(row.get(args.cjue_case_col, ""))
        if not case:
            continue
        cjue_cases_in_corpus.add(case)
        cjue_penal[case] = (row.get(args.cjue_penal_col) or "").strip()

# ======================================================
# 3) Construire la liste finale des affaires
#    - toutes celles du corpus
#    - + celles citées mais absentes du corpus
# ======================================================
all_cases = set(cjue_cases_in_corpus) | set(cited_by.keys())

# ======================================================
# 4) Écrire le CSV résultat
# ======================================================
out_fields = [
    "Numéro d'affaire",
    "Est cité par la chambre criminelle",
    "numeroAffaire",
    "Relatif au pénal",
]

with open(args.output, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=out_fields)
    writer.writeheader()

    for case in sorted(all_cases):
        crim_nums = cited_by.get(case, set())

        # nettoie/ordonne et retire éventuels "" parasites
        crim_nums = [x for x in sorted(crim_nums) if x]

        writer.writerow({
            "Numéro d'affaire": case,
            "Est cité par la chambre criminelle": "oui" if case in cited_by else "non",
            "numeroAffaire": "; ".join(crim_nums),
            "Relatif au pénal": cjue_penal.get(case, ""),
        })

print("✅ Terminé")
print(f"➡️ Affaires CJUE (corpus ∪ citations) : {len(all_cases)}")
print(f"📁 CSV généré : {args.output}")
