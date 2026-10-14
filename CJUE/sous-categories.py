'''import pandas as pd
import matplotlib.pyplot as plt

# Charger le corpus classifié
df = pd.read_csv("corpusv14/penal/corpusv14v2.csv", sep=';')

# Définition des sous-catégories pour chaque catégorie ciblée
ss_cat = {
    "Concurrence et consommation": [
        "Concurrence",
        "Protection des consommateurs"
    ],
    "Marché intérieur et liberté de circulation": [
        "Libre circulation des capitaux",
        "Libre circulation des marchandises",
        "Libre circulation des personnes",
        "Libre prestation des services",
        "Marché intérieur - Principes",
        "Marchés publics de l'Union européenne"
    ],
    "Institutions et principes fondamentaux de l’Union": [
        "Dispositions générales et finales",
        "Droit institutionnel",
        "Principes du droit de l'Union",
        "Privilèges et immunités",
        "Statut des fonctionnaires"
    ]
}

# Affichage des camemberts avec NOMBRE au lieu de %
for main_cat, subcats in ss_cat.items():
    mask_cat = df["Classification"].str.contains(main_cat, na=False)
    df_cat = df[mask_cat]
    
    counts = {sub: df_cat["Matières"].apply(lambda x: sub in str(x)).sum() for sub in subcats}
    
    # Supprimer les sous-catégories avec zéro arrêt pour éviter d'avoir des parts vides
    counts = {k: v for k, v in counts.items() if v > 0}
    
    # Fonction pour afficher les valeurs brutes
    def autopct_count(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f"{val}"
        return my_autopct
    
    plt.figure(figsize=(7,7))
    plt.pie(counts.values(), labels=counts.keys(), autopct=autopct_count(list(counts.values())))
    plt.title(f"Répartition des arrêts par sous-catégorie – {main_cat}")
    plt.tight_layout()
    plt.show()

#################

import pandas as pd
import matplotlib.pyplot as plt

# Charger le corpus classifié
df = pd.read_csv("corpusv14/penal/corpusv14v2.csv", sep=';')

# Sous-catégories pour chaque catégorie principale
ss_cat = {
    "Concurrence et consommation": [
        "Concurrence",
        "Protection des consommateurs"
    ],
    "Marché intérieur et liberté de circulation": [
        "Libre circulation des capitaux",
        "Libre circulation des marchandises",
        "Libre circulation des personnes",
        "Libre prestation des services",
        "Marché intérieur - Principes",
        "Marchés publics de l'Union européenne"
    ],
    "Institutions et principes fondamentaux de l’Union": [
        "Dispositions générales et finales",
        "Droit institutionnel",
        "Principes du droit de l'Union",
        "Privilèges et immunités",
        "Statut des fonctionnaires"
    ]
}

for main_cat, subcats in ss_cat.items():
    # Filtrer les textes de cette catégorie
    mask_cat = df["Classification"].str.contains(main_cat, na=False)
    df_cat = df[mask_cat]
    
    combo_counts = {}
    
    for _, row in df_cat.iterrows():
        matched_subs = [sub for sub in subcats if sub in str(row["Matières"])]
        if matched_subs:
            combo_name = " + ".join(matched_subs)
            combo_counts[combo_name] = combo_counts.get(combo_name, 0) + 1
    
    # Supprimer les combinaisons à 0
    combo_counts = {k: v for k, v in combo_counts.items() if v > 0}
    
    # Fonction pour afficher les nombres bruts
    def autopct_count(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{val}"
        return my_autopct
    
    # Camembert
    plt.figure(figsize=(7,7))
    plt.pie(combo_counts.values(), labels=combo_counts.keys(), autopct=autopct_count(list(combo_counts.values())))
    plt.title(f"Répartition des arrêts par sous-catégorie – {main_cat}")
    plt.tight_layout()
    plt.show()
'''

import pandas as pd

# Charger le corpus classifié
df = pd.read_csv("corpus_update/v5/corpus.csv", sep=",")

# Préparer les colonnes utilisées
for col in ["Classification", "Matières", "Texte interprété", "Sous-classification"]:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].fillna("")

# Sous-catégories (ordre = ordre d’itération et d’affichage)
ss_cat = {
    "Concurrence et consommation": [
        "Concurrence",
        "Protection des consommateurs"
    ],
    "Marché intérieur et liberté de circulation": [
        "Libre circulation des capitaux",
        "Libre circulation des marchandises",
        "Libre circulation des personnes",
        "Libre prestation des services",
        "Marché intérieur - Principes",
        "Marchés publics de l'Union européenne"
    ],
    "Institutions et principes fondamentaux de l’Union": [
        "Dispositions générales et finales",
        "Droit institutionnel",
        "Principes du droit de l'Union",
        "Privilèges et immunités",
        "Statut des fonctionnaires"
    ],
    "Coopération": [
        "MAE",
        "Convention de Bruxelles du 27 septembre 1968",
        "Coopération renforcée",
        "Espace de liberté, de sécurité et de justice",
        "Justice et affaires intérieures",
        "Procédure judiciaire"
    ],
    "Rapprochement des législations": [
        "Marchés publics",
        "Produits chimiques",
        "Technologies de l'information et de la communication"
    ],
    "Agriculture et pêche": [
        "Agriculture",
        "Pêche"
    ],
    "Fiscalité et douane": [
        "Fiscalité",
        "Union douanière et tarif douanier commun"
    ]
}

def norm(s: str) -> str:
    """Normalise pour comparaisons robustes (espaces insécables, apostrophes, casse)."""
    s = str(s)
    return " ".join(
        s.replace("\u00A0", " ").replace("’", "'").lower().split()
    )

def row_subcats(row) -> str:
    """Retourne la liste (join '; ') des sous-catégories correspondantes pour la ligne."""
    cl = norm(row["Classification"])
    mat = norm(row["Matières"])
    txt = norm(row["Texte interprété"])

    found = []

    # Conserver d'éventuelles sous-classifications déjà présentes (on merge)
    existing = [sc.strip() for sc in str(row["Sous-classification"]).split(";") if sc.strip()]
    for sc in existing:
        if sc not in found:
            found.append(sc)

    for main_cat, subcats in ss_cat.items():
        if norm(main_cat) in cl:  # "in" sur Classification (qui peut contenir plusieurs valeurs)
            for sub in subcats:
                if sub == "MAE":
                    is_mae = ("2002/584/jai du conseil" in txt)
                    if is_mae and sub not in found:
                        found.append(sub)
                else:
                    if norm(sub) in mat and sub not in found:
                        found.append(sub)

    return "; ".join(found)

# Calcul des sous-catégories (accumulation → chaîne séparée par '; ')
df["Sous-classification"] = df.apply(row_subcats, axis=1)

# Sauvegarde
df.to_csv("/Users/mariuspascal/Desktop/CJUE/corpus_update/v6/corpus.csv", index=False)
print("✅ Sous-classifications ajoutées (accumulation avec '; ') et fichier sauvegardé : corpusv14_mergev4.csv")
