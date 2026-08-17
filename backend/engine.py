# =====================================
# AZ TURF PRO - MOTEUR D'INTELLIGENCE
# engine.py
# =====================================

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def generer_badges_et_radar(cheval, info_course):
    """
    Génère les badges visuels et les notes sur 100 pour le graphique Radar.
    """
    badges = []
    info_c = info_course if isinstance(info_course, dict) else {}
    
    # --- BADGES INTELLIGENTS ---
    # 1. Pieds Nus (Trot)
    deferre = str(cheval.get("deferre", "")).upper()
    if deferre in ["D4", "DP_DG"]:
        badges.append({"code": "D4", "libelle": "Déferré D4", "couleur": "#28a745"})

    # 2. Duo Chaud
    taux_jockey = float(cheval.get("reussite_jockey", 0) or 0)
    confiance_ent = int(cheval.get("confiance_entraineur", 1) or 1)
    if taux_jockey >= 35 or confiance_ent == 2:
        badges.append({"code": "DUO_HOT", "libelle": "Duo Chaud 🔥", "couleur": "#ffc107"})

    # 3. Spécialiste Tracé
    hippodrome = str(info_c.get("hippodrome", "")).upper()
    hippo_fav = str(cheval.get("hippodromes_favoris", "")).upper()
    if hippodrome and hippodrome in hippo_fav:
        badges.append({"code": "TRACEE", "libelle": "Spécialiste 🎯", "couleur": "#17a2b8"})

    # 4. Rachat Imminent
    musique = str(cheval.get("musique", "")).upper()
    cote = float(cheval.get("cote", 20) or 20)
    if ("DA" in musique or "DISQ" in musique) and cote < 8.0:
        badges.append({"code": "RACHAT", "libelle": "Rachat ⚡", "couleur": "#fd7e14"})

    # --- PILIERS RADAR (Notes sur 100) ---
    forme = min(100, float(cheval.get("forme", 5) or 5) * 10)
    
    dist_course = int(info_c.get("distance", 2000) or 2000)
    dist_pref = int(cheval.get("distance_predilection", dist_course) or dist_course)
    aptitude_dist = max(20, 100 - (abs(dist_course - dist_pref) // 5))
    
    jockey_score = min(100, max(30, taux_jockey * 2))
    
    gains = float(cheval.get("gains_carriere", 0) or 0)
    courses = max(int(cheval.get("nombre_courses", 1) or 1), 1)
    classe_valeur = min(100, max(20, int((gains / courses) / 100)))
    
    jours_repos = int(cheval.get("jours_depuis_derniere_course", 20) or 20)
    fraicheur = 100 if 12 <= jours_repos <= 30 else (50 if jours_repos > 90 else 75)

    radar = {
        "forme": round(forme),
        "distance": round(aptitude_dist),
        "jockey": round(jockey_score),
        "classe": round(classe_valeur),
        "fraicheur": round(fraicheur)
    }

    return badges, radar


def calculer_indice_premium(cheval, info_course=None, discipline="TROT"):
    """
    Calcul élargi de l'indice Premium avec intégration des critères avancés.
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

    bonus_outsider_chaud = 15.0 if cote >= 10.0 and (forme >= 7.0 or regularite >= 7.0) else 0.0

    return round(
        indice_az + (forme * 1.35) + (regularite * 1.20) + (cote * 1.10) 
        + (experience * 0.80) + (bonnes_places * 2.0) + bonus_outsider_chaud, 2
    )


def lancer_analyse(chevaux, info_course=None):
    if not chevaux:
        return {"message": "Aucun cheval analysé", "chevaux": [], "classement": [], "tickets": {}, "non_partants": []}

    # 1. Filtrage des non-partants
    non_partants = (info_course or {}).get("non_partants", []) if isinstance(info_course, dict) else []
    np_nums = {str(np.get("numero")) if isinstance(np, dict) else str(np) for np in non_partants if np is not None}

    discipline = (info_course or {}).get("discipline", "TROT") if isinstance(info_course, dict) else "TROT"
    chevaux_scores = []

    # 2. Analyse et enrichissement
    for cheval in chevaux:
        num = str(cheval.get("numero", ""))
        est_np = num in np_nums or cheval.get("statut") == "NON_PARTANT"

        if est_np:
            np_nums.add(num)
            score_base, score_premium = -999.0, -999.0
            badges, radar = [], {}
        else:
            score_base = calculer_score_az(cheval, discipline=discipline)
            score_premium = calculer_indice_premium(cheval, info_course=info_course, discipline=discipline)
            badges, radar = generer_badges_et_radar(cheval, info_course)

        entree = dict(cheval)
        entree.update({
            "numero": cheval.get("numero"),
            "nom": cheval.get("nom", ""),
            "est_non_partant": est_np,
            "indice_az": score_base,
            "indice_premium": score_premium,
            "badges": badges,
            "radar": radar
        })
        chevaux_scores.append(entree)

    # 3. Classement & Tickets
    classement_complet = classer_chevaux(chevaux_scores)
    chevaux_valides = [c for c in classement_complet if not c.get("est_non_partant")]
    tickets = generer_tickets_az(chevaux_valides)
    
    liste_np = sorted(list(np_nums), key=lambda x: int(x) if str(x).isdigit() else 9999)

    # 4. Enregistrement apprentissage
    try:
        enregistrer_course({
            "chevaux": chevaux_valides,
            "classement": classement_complet,
            "tickets": tickets,
            "course": info_course or {}
        })
    except Exception:
        pass

    return {
        "message": "Analyse AZ Turf Pro terminée",
        "chevaux": classement_complet,
        "classement": classement_complet,
        "non_partants": liste_np,
        "texte_non_partants": f"Non-partant(s) : {', '.join(liste_np)}" if liste_np else "Aucun non-partant",
        "favori": chevaux_valides[0] if chevaux_valides else {},
        "tickets": tickets
    }
