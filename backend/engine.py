# =====================================
# AZ TURF PRO - MOTEUR D'INTELLIGENCE
# engine.py
# =====================================

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def calculer_indice_premium(cheval, info_course=None, discipline="TROT"):
    """
    Indice Premium : combine l'Indice AZ d'origine avec l'analyse experte globale :
    - Aptitude distance, déférage, œillères, fraîcheur, retard de gains, rachat échec.
    """
    indice_az = float(cheval.get("indice_az", 0) or 0)
    forme = float(cheval.get("forme", 5) or 5)
    regularite = float(cheval.get("regularite", 5) or 5)
    cote = float(cheval.get("cote", 5) or 5)
    experience = float(cheval.get("experience", 5) or 5)
    
    bonnes_places = sum(
        1 for p in (cheval.get("performances") or []) 
        if isinstance(p, (int, float)) and p <= 3
    )

    bonus_outsider_chaud = 0.0
    if cote >= 10.0 and (forme >= 7.0 or regularite >= 7.0):
        bonus_outsider_chaud = 15.0

    bonus_expert = 0.0
    info_c = info_course if isinstance(info_course, dict) else {}

    # 1. Aptitude à la distance
    dist_course = int(info_c.get("distance", 2000) or 2000)
    dist_pref = int(cheval.get("distance_predilection", dist_course) or dist_course)
    if abs(dist_course - dist_pref) <= 200:
        bonus_expert += 10.0

    # 2. Déférage (Trot)
    deferre = str(cheval.get("deferre", "")).upper()
    if deferre in ["D4", "DP_DG"]:
        bonus_expert += 12.0
    elif deferre in ["DA", "DP"]:
        bonus_expert += 6.0

    # 3. Œillères & Équipement
    oeilleres = str(cheval.get("oeilleres", "")).upper()
    if "OEI" in oeilleres or "FERMEES" in oeilleres:
        bonus_expert += 8.0

    # 4. Retard de gains
    gains = float(cheval.get("gains_carriere", 0) or 0)
    courses = max(int(cheval.get("nombre_courses", 1) or 1), 1)
    if (gains / courses) > 8000:
        bonus_expert += 10.0

    # 5. Rachat après échec (DA/Disq + Cote basse)
    musique = str(cheval.get("musique", "")).upper()
    if ("DA" in musique or "DISQ" in musique) and cote < 8.0:
        bonus_expert += 10.0

    # 6. Fraîcheur / Repos (12 à 30 jours)
    jours_repos = int(cheval.get("jours_depuis_derniere_course", 20) or 20)
    if 12 <= jours_repos <= 30:
        bonus_expert += 8.0

    return round(
        indice_az
        + (forme * 1.35)
        + (regularite * 1.20)
        + (cote * 1.10)
        + (experience * 0.80)
        + (bonnes_places * 2.0)
        + bonus_outsider_chaud
        + bonus_expert,
        2
    )


def lancer_analyse(chevaux, info_course=None):
    """
    Orchestre l'analyse complète d'une course.
    Conserve les non-partants dans le tableau (marqués comme NP) mais les exclut des tickets.
    """
    if not chevaux:
        return {
            "message": "Aucun cheval analysé",
            "chevaux": [],
            "classement": [],
            "tickets": {},
            "non_partants": [],
        }

    # =========================================================
    # 1. IDENTIFICATION DES NON-PARTANTS
    # =========================================================
    non_partants = []
    if info_course and isinstance(info_course, dict):
        non_partants = info_course.get("non_partants", [])

    np_nums = set()
    for np in non_partants:
        if isinstance(np, dict):
            num = np.get("numero")
            if num is not None:
                np_nums.add(str(num))
        elif np is not None:
            np_nums.add(str(np))

    discipline = "TROT"
    if info_course and isinstance(info_course, dict):
        discipline = info_course.get("discipline", "TROT")

    chevaux_scores = []

    # =========================================================
    # 2. CALCUL DES SCORES POUR TOUS LES CHEVAUX (AVEC MARQUAGE NP)
    # =========================================================
    for cheval in chevaux:
        num = str(cheval.get("numero", ""))
        est_np = num in np_nums or cheval.get("statut") == "NON_PARTANT"

        if est_np:
            np_nums.add(num)
            score_base = -999.0
            score_premium = -999.0
        else:
            score_base = calculer_score_az(cheval, discipline=discipline)
            score_premium = calculer_indice_premium(cheval, info_course=info_course, discipline=discipline)
        
        entree = dict(cheval)
        entree["numero"] = cheval.get("numero")
        entree["nom"] = cheval.get("nom", "")
        entree["est_non_partant"] = est_np
        entree["indice_az"] = score_base
        entree["indice_premium"] = score_premium
        chevaux_scores.append(entree)

    # 3. Classement complet (les non-partants se retrouvent en fin de tableau)
    classement_complet = classer_chevaux(chevaux_scores)

    # 4. Filtrage STRICT pour la génération des tickets uniquement
    chevaux_valides_pour_tickets = [c for c in classement_complet if not c.get("est_non_partant")]
    tickets = generer_tickets_az(chevaux_valides_pour_tickets)

    # Liste triée des numéros non-partants pour l'affichage Accueil
    liste_np_ordonnee = sorted(list(np_nums), key=lambda x: int(x) if str(x).isdigit() else 9999)

    # 5. Sauvegarde dans le module d'apprentissage
    try:
        enregistrer_course({
            "chevaux": chevaux_valides_pour_tickets,
            "classement": classement_complet,
            "tickets": tickets,
            "selection_az": (tickets.get("gratuit") or {}).get("quinte", []),
            "course": info_course or {},
        })
    except Exception:
        pass

    return {
        "message": "Analyse AZ Turf Pro terminée",
        "chevaux": classement_complet,
        "classement": classement_complet,
        "partants_complets": chevaux,
        "non_partants": liste_np_ordonnee,
        "texte_non_partants": f"Non-partant(s) : {', '.join(liste_np_ordonnee)}" if liste_np_ordonnee else "Aucun non-partant",
        "favori": chevaux_valides_pour_tickets[0] if chevaux_valides_pour_tickets else {},
        "tickets": tickets,
        }
