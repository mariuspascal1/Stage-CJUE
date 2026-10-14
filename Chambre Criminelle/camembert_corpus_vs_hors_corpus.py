import argparse
import csv
import sys
import matplotlib.pyplot as plt

# ======================================================
# CLI
# ======================================================
parser = argparse.ArgumentParser(
    description="Camembert: affaires CJUE citées par la chambre criminelle selon présence dans le corpus CJUE"
)
parser.add_argument("--input", required=True, help="CSV d'entrée (affaires citées uniquement)")
parser.add_argument("--output", default=None, help="(Optionnel) Chemin PNG de sortie. Si absent: affichage écran.")
parser.add_argument("--col", default="Présent dans le corpus CJUE", help="Nom de la colonne oui/non")
args = parser.parse_args()

# ======================================================
# CSV field size (au cas où)
# ======================================================
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(10_000_000)

# ======================================================
# Comptage
# ======================================================
counts = {"oui": 0, "non": 0, "autre/vides": 0}

with open(args.input, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        raise ValueError("❌ CSV sans en-têtes")

    if args.col not in reader.fieldnames:
        raise ValueError(f"❌ Colonne '{args.col}' introuvable. Colonnes dispo: {reader.fieldnames}")

    for row in reader:
        v = (row.get(args.col) or "").strip().lower()
        if v == "oui":
            counts["oui"] += 1
        elif v == "non":
            counts["non"] += 1
        else:
            counts["autre/vides"] += 1

labels = ["Présents dans le corpus CJUE", "Hors corpus CJUE"]
values = [counts["oui"], counts["non"]]

# Si jamais il y a des valeurs inattendues, on les ajoute au graphe
if counts["autre/vides"] > 0:
    labels.append("Autre / vide")
    values.append(counts["autre/vides"])

total = sum(values)
if total == 0:
    raise ValueError("❌ Aucun enregistrement comptabilisé (total=0). Vérifie le CSV / la colonne.")

# ======================================================
# Plot camembert
# ======================================================
plt.figure(figsize=(7, 7))
plt.pie(
    values,
    labels=labels,
    colors=["#70e1e6", "#f4a261"],
    autopct=lambda p: f"{p:.1f}%\n({int(round(p*total/100))})",
    startangle=90
)

plt.title("Répartition des affaires CJUE citées par la chambre criminelle\nselon leur présence dans le corpus CJUE", pad=20)
plt.tight_layout()

# ======================================================
# Save / Show
# ======================================================
if args.output:
    plt.savefig(args.output, dpi=200)
    print("✅ Camembert enregistré")
    print(f"📁 Fichier : {args.output}")
else:
    plt.show()

print(f"➡️ Total : {total} (oui={counts['oui']}, non={counts['non']}, autre/vides={counts['autre/vides']})")
