# =====================================
# AZ TURF PRO
# MOTEUR D'ANALYSE COMPLET (engine.py)
# =====================================

def calculer_score_gratuit(cheval, info_course):
    """
    Analyse de base pour les utilisateurs gratuits (Cote + Musique simple)
    """
    score = 0.0
    
    # 1. Musique simple
    musique = str(cheval.get("musique", "")).upper()
    if "1P" in musique or "1A" in musique or "1M" in musique:
        score += 10
    elif "2P" in musique or "3P" in musique:
        score += 5

    # 2. Cote du marché
    cote = float(cheval.get("cote", 20))
    if 0 < cote <= 5.0:
        score += 15
    elif 5.0 < cote <= 10.0:
        score += 8

    return round(score, 2)


def calculer_score_premium_expert(cheval, info_course):
    """
    Analyse ultra-poussée avec TOUS les critères experts réservée au Premium
    """
    score = 0.0

    # 1. Aptitude à la distance (0 à 15 pts)
    distance_course = int(info_course.get("distance", 2000) or 2000)
    dist_pref = int(cheval.get("distance_predilection", distance_course))
    ecart_dist = abs(distance_course - dist_pref)
    
    if ecart_dist == 0:
        score += 15
    elif ecart_dist <= 200:
        score += 10
    elif ecart_dist <= 400:
        score += 5

    # 2. Déférage (Critère majeur au Trot) (0 à 15 pts)
    deferre = str(cheval.get("deferre", "")).upper()
    if deferre in ["D4", "DP_DG"]:
        score += 15
    elif deferre in ["DA", "DP"]:
        score += 8

    # 3. Œillères & Équipement (0 à 10 pts)
    oeilleres = str(cheval.get("oeilleres", "")).upper()
    if "OEI" in oeilleres or "FERMEES" in oeilleres:
        score += 10
    elif "AUSTRALIAN" in oeilleres or "OEA" in oeilleres:
        score += 5

    # 4. Forme récente & Musique (0 à 15 pts)
    musique = str(cheval.get("musique", "")).upper()
    if "1P" in musique or "1T" in musique or "1A" in musique or "1M" in musique:
        score += 15
    elif "2P" in musique or "3P" in musique:
        score += 12
    elif "4P" in musique or "5P" in musique:
        score += 8

    # 5. Forme Jockey/Driver & Confiance Entraîneur (0 à 15 pts)
    taux_jockey = float(cheval.get("reussite_jockey", 50))
    score += (taux_jockey / 100) * 10
    
    confiance_entraineur = int(cheval.get("confiance_entraineur", 1))
    if confiance_entraineur == 2:
        score += 5

    # 6. Retard de gains & Valeur (0 à 15 pts)
    gains = float(cheval.get("gains_carriere", 0))
    courses = max(int(cheval.get("nombre_courses", 1)), 1)
    gain_moyen = gains / courses
    
    if gain_moyen > 10000:
        score += 15
    elif gain_moyen > 5000:
        score += 10

    # 7. Leçons des échecs passés / Signal de Rachat (0 à 12 pts)
    cote = float(cheval.get("cote", 20))
    if ("DA" in musique or "DISQ" in musique or "0P" in musique) and cote < 8.0:
        score += 12  # Détection d'un échec accidentel corrigé par l'entourage

    # 8. Fraîcheur / Intervalle de repos (0 à 10 pts)
    jours_repos = int(cheval.get("jours_depuis_derniere_course", 20))
    if 12 <= jours_repos <= 30:
        score += 10  # Condition physique optimale
    elif jours_repos > 90:
        score -= 5   # Manque de compétition (Rentrée)

    # 9. Aptitude à l'hippodrome (0 à 10 pts)
    hippodrome_actuel = str(info_course.get("hippodrome", "")).upper()
    hippodromes_gagnes = str(cheval.get("hippodromes_favoris", "")).upper()
    if hippodrome_actuel and hippodrome_actuel in hippodromes_gagnes:
        score += 10

    # 10. Cotes et Enjeux du marché (0 à 15 pts)
    if 0 < cote <= 4.0:
        score += 15
    elif 4.0 < cote <= 8.0:
        score += 10
    elif 8.0 < cote <= 15.0:
        score += 5

    return round(score, 2)


# =====================================
# LANCEUR D'ANALYSE PRINCIPAL
# =====================================

def lancer_analyse(chevaux, info_course, est_premium=False):
    """
    Fonction principale appelée par api.py
    Gère le filtrage des non-partants, le tri et la génération des tickets
    """
    chevaux_analyses = []
    non_partants_officiels = [str(np) for np in info_course.get("non_partants", [])]

    for cheval in chevaux:
        num_str = str(cheval.get("numero", ""))
        
        # Isolation des non-partants
        if num_str in non_partants_officiels or cheval.get("statut") == "NON_PARTANT":
            c_copy = dict(cheval)
            c_copy["score_az"] = -999.0
            c_copy["est_non_partant"] = True
            chevaux_analyses.append(c_copy)
            continue

        # Calcul selon la formule choisie (Gratuit ou Premium Expert)
        if est_premium:
            score = calculer_score_premium_expert(cheval, info_course)
        else:
            score = calculer_score_gratuit(cheval, info_course)

        c_copy = dict(cheval)
        c_copy["score_az"] = score
        c_copy["est_non_partant"] = False
        chevaux_analyses.append(c_copy)

    # Tri des chevaux par score décroissant (les non-partants finissent en dernier)
    chevaux_analyses.sort(key=lambda x: x.get("score_az", -999.0), reverse=True)

    # Extraction exclusive des vrais partants valides
    partants_valides = [
        str(c.get("numero", "")) 
        for c in chevaux_analyses 
        if not c.get("est_non_partant")
    ]

    # Attribution de l'ordre de classement
    rang = 1
    for c in chevaux_analyses:
        if not c.get("est_non_partant"):
            c["rang"] = rang
            rang += 1
        else:
            c["rang"] = "NP"

    # Generation des pronostics et tickets
    tickets = {
        "favori": partants_valides[0] if len(partants_valides) > 0 else "",
        "base_solide": partants_valides[:2],
        "gratuit_trio": partants_valides[:3]
    }

    # Desormais accessible aux comptes Premium
    if est_premium:
        tickets["couple_vip"] = partants_valides[:3]
        tickets["tierce_premium"] = partants_valides[:4]
        tickets["quarte_premium"] = partants_valides[:5]
        tickets["quinte_vip"] = partants_valides[:8]

    return {
        "chevaux": chevaux_analyses,
        "tickets": tickets
        }
