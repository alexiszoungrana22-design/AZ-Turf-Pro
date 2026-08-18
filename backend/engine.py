"""
=========================================================
AZ TURF PRO - MOTEUR D'INTELLIGENCE
=========================================================

Fichier complet : engine.py
- Conservation de la structure et du filtrage d'origine
- Ajout du générateur de Badges Intelligents
- Ajout des notes pour le graphique Radar (5 piliers)
- Intégration des critères d'analyse Premium enrichis
=========================================================
"""

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def generer_badges_et_radar(cheval, info_course=None):
    """
    Génère les badges visuels dynamiques et les notes sur 100 pour le graphique Radar.
    Ne modifie en rien la logique d'analyse.
    """
    badges = []
    info_c = info_course if isinstance(info_course, dict) else {}

    # --- 1. BADGES INTELLIGENTS ---
    deferre = str(cheval.get("deferre", "") or "").strip().upper()
    if deferre in ("D4", "DP_DG"):
        badges.append({"code": "D4", "libelle": "Déferré D4", "couleur": "#28a745"})
    elif deferre in ("DA", "DP"):
        badges.append({"code": "DP", "libelle": "Déferré", "couleur": "#17a2b8"})

    taux_jockey = float(cheval.get("reussite_jockey", 0) or 0)
    confiance_ent = int(cheval.get("confiance_entraineur", 1) or 1)
    if taux_jockey >= 35 or confiance_ent == 2:
        badges.append({"code": "DUO_HOT", "libelle": "Duo Chaud 🔥", "couleur": "#ffc107"})

    hippodrome = str(info_c.get("hippodrome", "") or "").strip().upper()
    hippo_fav = str(cheval.get("hippodromes_favoris", "") or "").strip().upper()
    if hippodrome and hippodrome in hippo_fav:
        badges.append({"code": "TRACEE", "libelle": "Spécialiste 🎯", "couleur": "#17a2b8"})

    musique = str(cheval.get("musique", "") or "").strip().upper()
    cote = float(cheval.get("cote", 20) or 20)
    if ("DA" in musique or "DISQ" in musique) and cote < 8.0:
        badges.append({"code": "RACHAT", "libelle": "Rachat ⚡", "couleur": "#fd7e14"})

    # --- 2. PILIERS RADAR (Notes de 0 à 100) ---
    forme = min(100.0, float(cheval.get("forme", 5) or 5) * 10.0)

    dist_course = int(info_c.get("distance", 2000) or 2000)
    dist_pref = int(cheval.get("distance_predilection", dist_course) or dist_course)
    aptitude_dist = max(20.0, 100.0 - (abs(dist_course - dist_pref) / 5.0))

    jockey_score = min(100.0, max(30.0, taux_jockey * 2.0))

    gains = float(cheval.get("gains_carriere", 0) or 0)
    courses = max(1, int(cheval.get("nombre_courses", 1) or 1))
    classe_valeur = min(100.0, max(20.0, (gains / courses) / 100.0))

    jours_repos = int(cheval.get("jours_depuis_derniere_course", 20) or 20)
    fraicheur = 100.0 if 12 <= jours_repos <= 30 else (50.0 if jours_repos > 90 else 75.0)

    radar = {
        "forme": round(forme, 1),
        "distance": round(aptitude_dist, 1),
        "jockey": round(jockey_score, 1),
        "classe": round(classe_valeur, 1),
        "fraicheur": round(fraicheur, 1)
    }

    return badges, radar


def calculer_indice_premium(cheval, info_course=None, discipline="TROT"):
    """
    Indice Premium : combine l'Indice AZ avec une analyse croisée de valeur et de critères experts.
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

    # Critères Experts additionnels
    bonus_expert = 0.0
    info_c = info_course if isinstance(info_course, dict) else {}

    # Aptitude à la distance
    dist_course = int(info_c.get("distance", 2000) or 2000)
    dist_pref = int(cheval.get("distance_predilection", dist_course) or dist_course)
    if abs(dist_course - dist_pref) <= 200:
        bonus_expert += 10.0

    # Déférage
    deferre = str(cheval.get("deferre", "") or "").strip().upper()
    if deferre in ("D4", "DP_DG"):
        bonus_expert += 12.0
    elif deferre in ("DA", "DP"):
        bonus_expert += 6.0

    # Œillères
    oeilleres = str(cheval.get("oeilleres", "") or "").strip().upper()
    if "OEI" in oeilleres or "FERMEES" in oeilleres:
        bonus_expert += 8.0

    # Retard de gains
    gains = float(cheval.get("gains_carriere", 0) or 0)
    courses = max(1, int(cheval.get("nombre_courses", 1) or 1))
    if (gains / courses) > 8000:
        bonus_expert += 10.0

    # Signal de rachat
    musique = str(cheval.get("musique", "") or "").strip().upper()
    if ("DA" in musique or "DISQ" in musique) and cote < 8.0:
        bonus_expert += 10.0

    # Fraîcheur
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
    Orchestre l'analyse complète d'une course en filtrant automatiquement les non-partants.
    """
    if not chevaux:
        return {
            "message": "Aucun cheval analysé",
            "chevaux": [],
            "classement": [],
            "tickets": {},
        }

    # =========================================================
    # 1. EXTRACTION ET FILTRAGE AUTOMATIQUE DES NON-PARTANTS
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

    # Exclusion stricte des non-partants de la liste des chevaux à analyser
    chevaux_valides = []
    for cheval in chevaux:
        num = cheval.get("numero")
        if num is not None and str(num) in np_nums:
            continue  # Ignore le cheval s'il est non-partant
        chevaux_valides.append(cheval)

    discipline = "TROT"
    if info_course and isinstance(info_course, dict):
        discipline = info_course.get("discipline", "TROT")

    chevaux_scores = []

    for cheval in chevaux_valides:
        score_base = calculer_score_az(cheval, discipline=discipline)
        
        entree = dict(cheval)
        entree["numero"] = cheval.get("numero")
        entree["nom"] = cheval.get("nom", "")
        entree["indice_az"] = score_base
        entree["indice_premium"] = calculer_indice_premium(entree, info_course=info_course, discipline=discipline)
        
        # Génération passive des Badges et du Radar
        badges, radar = generer_badges_et_radar(entree, info_course=info_course)
        entree["badges"] = badges
        entree["radar"] = radar

        chevaux_scores.append(entree)

    # 2. Classement des chevaux valides uniquement
    classement = classer_chevaux(chevaux_scores)
    
    # 3. Génération des tickets sans les non-partants
    tickets = generer_tickets_az(classement)

    # 4. Sauvegarde dans le module d'apprentissage
    try:
        enregistrer_course({
            "chevaux": chevaux_valides,
            "classement": classement,
            "tickets": tickets,
            "selection_az": (tickets.get("gratuit") or {}).get("quinte", []),
            "course": info_course or {},
        })
    except Exception:
        pass

    return {
        "message": "Analyse AZ Turf Pro (Mode Avancé) terminée",
        "chevaux": classement,
        "classement": classement,
        "partants_complets": chevaux,
        "non_partants": sorted(np_nums, key=lambda x: int(x) if str(x).isdigit() else 9999),
        "favori": classement[0] if classement else {},
        "tickets": tickets,
    }
