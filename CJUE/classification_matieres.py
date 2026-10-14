import pandas as pd

# === 1. Charger ton fichier CSV ===
# Remplace le chemin par celui de ton fichier local
df = pd.read_csv("corpus_update/v4/penal/corpusv4_1.csv", sep =",") 

# === 2. Extraire et nettoyer les matières ===
liste_matières = []
all_matières = ["Action extérieure",
 "accords internationaux",
 "Accords d'association",
 "aide humanitaire",
 "Association européenne de libre-échange (AELE)",
 "clause de solidarité",
 "Coopération au développement",
 "coopération économique, financière et technique avec les pays tiers",
 "Politique commerciale commune",
 "Accord général sur les tarifs douaniers et le commerce (GATT)",
 "Dumping",
 "Mesures de sauvegarde",
 "Organisation Mondiale du Commerce (OMC)",
 "Subventions",
 "Subventions étrangères faussant le marché intérieur",
 "Relations diplomatiques",
 "Adhésion de nouveaux États",
 "Agence d'approvisionnement",
 "Agriculture",
 "Fonds agricoles",
 "Législation phytosanitaire",
 "Législation vétérinaire",
 "Mesures monétaires en agriculture",
 "Montants compensatoires - Adhésion",
 "Organisation commune des marchés",
 "Paiements directs",
 "Association des pays et territoires d'outre-mer",
 "Balance des paiements",
 "Banque européenne d'investissement",
 "Clause compromissoire",
 "Cohésion économique, sociale et territoriale",
 "Fonds de cohésion",
 "Fonds européen de développement régional (FEDER)",
 "Combustibles - Charbon au sens large",
 "Concurrence",
 "Aides accordées par les États",
 "Concentrations entre entreprises",
 "Ententes",
 "Entreprises publiques",
 "Position dominante",
 "Contrôle de sécurité",
 "Convention de Bruxelles du 27 septembre 1968",
 "Compétence",
 "Exécution",
 "Convention de Lugano du 16 septembre 1988",
 "Convention de Rome du 19 juin 1980",
 "coopération administrative",
 "Coopération policière et judiciaire en matière pénale",
 "Coopération renforcée",
 "Culture",
 "Développement de la recherche",
 "Diffusion des connaissances",
 "Dispositions en application de l'article 95",
 "Dispositions financières",
 "Budget",
 "Cadre financier",
 "Lutte contre la fraude",
 "Péréquation de ferrailles",
 "Prélèvements et emprunts",
 "Prêts et subventions",
 "Ressources propres",
 "Dispositions générales et finales",
 "Dispositions sociales",
 "Droit des entreprises",
 "Droit institutionnel",
 "Actes des institutions",
 "Responsabilité non contractuelle",
 "Droits fondamentaux",
 "Charte des droits fondamentaux",
 "Emploi",
 "Ententes et concentrations",
 "Entreprises communes",
 "Environnement",
 "Déchets",
 "Pollution",
 "Échange de quotas d'émission de gaz à effet de serre",
 "Environnement et consommateurs",
 "espace de liberté, de sécurité et de justice",
 "Coopération judiciaire en matière civile",
 "coopération judiciaire en matière pénale",
 "coopération policière",
 "Frontières, asile et immigration",
 "Contrôles aux frontières",
 "politique d'asile",
 "Politique d'immigration",
 "Éducation, formation professionnelle, jeunesse et sport",
 "Énergie",
 "Énergie nucléaire",
 "État de pénurie",
 "Fiscalité",
 "Autres impôts indirects",
 "Impôts indirects sur les rassemblements de capitaux",
 "Droits d'accise",
 "Impositions intérieures",
 "Taxe sur la valeur ajoutée",
 "Fonds social européen (FSE)",
 "Informations et vérifications",
 "Investissements",
 "Justice et affaires intérieures",
 "Libre circulation des capitaux",
 "Libre circulation des marchandises",
 "Coopération douanière",
 "Code des douanes",
 "Propriété industrielle",
 "Restrictions quantitatives",
 "Mesures d'effet équivalent",
 "Monopoles nationaux",
 "Union douanière et tarif douanier commun",
 "Classement tarifaire",
 "Taxes d'effet équivalent",
 "Libre circulation des personnes",
 "Liberté d'établissement",
 "Libre circulation des travailleurs",
 "Sécurité sociale",
 "Libre prestation des services",
 "Marché commun nucléaire",
 "Marché intérieur - Principes",
 "Marchés publics de l'Union européenne",
 "Non-discrimination et citoyenneté de l'Union",
 "Citoyenneté de l'Union",
 "Droit d'entrée et de séjour",
 "non-discrimination",
 "Non-discrimination en raison de la nationalité",
 "Pêche",
 "Politique de conjoncture",
 "Politique économique et monétaire",
 "Banque centrale européenne (BCE)",
 "Euro",
 "Surveillance des établissements de crédit",
 "Système européen de banques centrales",
 "Politique étrangère et de sécurité commune",
 "Mesures restrictives",
 "Politique industrielle",
 "Politique régionale",
 "Politique sociale",
 "Égalité de traitement",
 "Principes du droit de l'Union",
 "Accès aux documents",
 "Protection des données à caractère personnel",
 "Privilèges et immunités",
 "Procédure judiciaire",
 "Procédures particulières",
 "Production",
 "Propriété intellectuelle, industrielle et commerciale",
 "Brevets",
 "Dessins et modèles",
 "Droit d'auteur et droits voisins",
 "Marques",
 "Obtentions végétales",
 "protection civile",
 "Protection des consommateurs",
 "Protection sanitaire",
 "Questions procédurales",
 "Rapprochement des législations",
 "Assurances",
 "Marchés publics",
 "Normes et réglementations techniques",
 "Produits chimiques",
 "Enregistrement, évaluation, autorisation et restrictions applicables aux substances chimiques (règlement REACH)",
 "Produits pharmaceutiques et cosmétiques",
 "Régime fiscal commun des entreprises",
 "Régulation des marchés et services numériques",
 "Régulation des marchés numériques",
 "Régulation des services numériques",
 "Services financiers",
 "Sécurité alimentaire",
 "Technologies de l'information et de la communication",
 "Recherche, développement technologique et espace",
 "espace",
 "Recherche, informations, éducation, statistiques",
 "Régime de propriété",
 "Régime du secret",
 "Réseaux transeuropéens",
 "Santé publique",
 "Sidérurgie - Acier au sens large",
 "Aides accordées par les États",
 "Prix",
 "Quotas de production",
 "Régime de surveillance",
 "Statut des fonctionnaires",
 "Tarif unifié commun",
 "tourisme",
 "Transports",
 "Indemnisation et assistance des passagers",
 "Sécurité aérienne"]

cat1 = ["Action extérieure", "Association des pays et territoires d'outre-mer", "Politique étrangère et de sécurité commune"]
cat2 = ["Adhésion de nouveaux États", "Non-discrimination et citoyenneté de l'Union"]
cat3 = ["Agriculture", "Pêche"]
cat4 = ["Balance des paiements", "Banque européenne d'investissement", "Dispositions financières", "Politique économique et monétaire"]
cat5 = ["Politique industrielle", "Sidérurgie - Acier au sens large"]
cat6 = ["Fiscalité", "Union douanière et tarif douanier commun"]
cat7 = ["Environnement", "Énergie", "Santé publique"]
cat8 = ["Concurrence", "Protection des consommateurs"]
cat9 = ["Libre circulation des capitaux", "Libre circulation des marchandises", "Libre circulation des personnes", "Libre prestation des services", "Marché intérieur - Principes", "Marchés publics de l'Union européenne"]
cat10 = ["Droits fondamentaux"]
cat11 = ["Convention de Bruxelles du 27 septembre 1968", "Coopération renforcée", "Coopération judiciaire en matière civile", "coopération judiciaire en matière pénale", "coopération policière", "Justice et affaires intérieures", "Procédure judiciaire"]
cat12 = ["Frontières, asile et immigration"]
cat13 = ["Dispositions générales et finales", "Droit institutionnel", "Principes du droit de l'Union", "Privilèges et immunités", "Statut des fonctionnaires"]
cat14 = ["Cohésion économique, sociale et territoriale", "Éducation, formation professionnelle, jeunesse et sport", "Fonds social européen (FSE)", "Politique sociale"]
cat15 = ["Rapprochement des législations"]
cat16 = ["Recherche, développement technologique et espace", "Réseaux transeuropéens", "Transports"]
cat17 = ["Régime de propriété", "Propriété intellectuelle, industrielle et commerciale"]

# Dictionnaire de correspondance
categories = {
    "Action extérieure et politique étrangère": cat1,
    "Non-discrimination, citoyenneté de l’Union et élargissement": cat2,
    "Agriculture et pêche": cat3,
    "Politique économique et monétaire": cat4,
    "Politique industrielle": cat5,
    "Fiscalité et douane": cat6,
    "Environnement, énergie et santé": cat7,
    "Concurrence et consommation": cat8,
    "Marché intérieur et liberté de circulation": cat9,
    "Droits fondamentaux": cat10,
    "Coopération": cat11,
    "Frontières": cat12,
    "Institutions et principes fondamentaux de l’Union": cat13,
    "Cohésion économique, sociale et territoriale": cat14,
    "Rapprochement des législations": cat15,
    "Transports et espace": cat16,
    "Propriété": cat17
}

# Fonction pour classifier une ligne
def classify_matière(line):
    if pd.isna(line):
        return None

    found_categories = []

    for cat_name, keywords in categories.items():
        for keyword in keywords:
            if keyword in line:
                found_categories.append(cat_name)
                break  # Évite les doublons pour une même catégorie

    if not found_categories:
        return None
    elif len(found_categories) == 1:
        return found_categories[0]
    else:
        return "; ".join(found_categories)

# Appliquer au DataFrame
df["Classification"] = df["Matières"].apply(classify_matière)



# === 3. Sauvegarder le df
df.to_csv("corpus_update/v5/corpus.csv", index=False)
