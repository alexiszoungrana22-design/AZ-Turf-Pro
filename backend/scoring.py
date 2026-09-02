"""
AZ TURF PRO - SCORING AVANCÉ (Optimisé 85%)
Fichier complet à remplacer : scoring.py

Enrichi avec des critères propres à chacune des 4 spécialités reconnues par
le PMU : Plat, Trot attelé, Trot monté, Obstacle (haies/steeple/cross).
Auparavant, Attelé et Monté étaient confondus sous un seul bucket "TROT" ;
ils ont des dynamiques différentes (le jockey pèse davantage en monté qu'en
attelé) et sont désormais distingués. Le bonus corde (Plat) et le bonus
déferrage (Trot) existaient déjà mais ne recevaient jamais de valeur car
pmu_source.py n'extrayait pas ces champs — corrigé côté extraction, ce
fichier peut donc désormais réellement les exploiter.
"""


def _num(valeur, defaut=0.0):
    """Conversion sûre vers float : traite aussi bien une clé absente
    qu'une valeur explicitement None ou vide (jamais renvoyée telle
    quelle dans un calcul, contrairement à dict.get(cle, defaut))."""
    if valeur is None or valeur == "":
        return defaut
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return defaut


def classifier_discipline(discipline):
    """Classe la discipline PMU brute en l'une des 4 spécialités reconnues :
    "PLAT", "ATTELE", "MONTE", "OBSTACLE". Ne suppose jamais un format PMU
    exact : classification par mots-clés (robuste aux variantes d'écriture),
    avec un repli neutre si la donnée est absente ou non reconnue."""
    disc = str(discipline or "").upper()
    if "PLAT" in disc:
        return "PLAT"
    if "MONTE" in disc:
        return "MONTE"
    if "TROT" in disc or "ATTELE" in disc:
        return "ATTELE"
    if disc:
        return "OBSTACLE"  # HAIES, STEEPLE-CHASE, CROSS, etc.
    return "ATTELE"  # discipline inconnue : repli neutre (la plus courante en France)


def calculer_score_az(cheval, discipline="TROT"):
    """
    Calcule l'indice AZ avec pondération dynamique selon la spécialité.
    """
    score = 0
    specialite = classifier_discipline(discipline)

    # --- 1. PONDÉRATION PAR SPÉCIALITÉ ---
    if specialite == "ATTELE":
        # Le driver influence directement l'allure (pas de monte), le
        # déferrage est un facteur technique déterminant.
        coef_forme = 4.5
        coef_regularite = 4.0
        coef_jockey = 3.5  # Driver
        coef_cote = 2.5
        coef_experience = 2.0
    elif specialite == "MONTE":
        # Champs plus techniques et souvent plus réduits qu'à l'attelé ;
        # le jockey (equilibre, tactique de course) pèse davantage, et les
        # chevaux de monté sont en moyenne plus expérimentés.
        coef_forme = 4.0
        coef_regularite = 4.0
        coef_jockey = 5.0  # Jockey (poids sur le dos, pilotage)
        coef_cote = 2.5
        coef_experience = 2.5
    elif specialite == "PLAT":
        coef_forme = 5.5
        coef_regularite = 3.0
        coef_jockey = 4.0  # Jockey & Corde
        coef_cote = 3.0
        coef_experience = 1.5
    else:  # OBSTACLE / HAIES / STEEPLE / CROSS
        # L'expérience du saut et la régularité priment sur la pure vitesse.
        coef_forme = 4.0
        coef_regularite = 5.0
        coef_jockey = 3.0
        coef_cote = 2.0
        coef_experience = 4.0

    # --- 2. CALCUL DE BASE ---
    # _num() protège contre une valeur explicitement None dans le dict (pas
    # seulement une clé absente) : cheval.get("forme", 0) renvoie None, pas
    # 0, si "forme" existe mais vaut None — ce qui faisait planter le calcul
    # avec de vraies données PMU incomplètes (cote/forme non documentées
    # pour certains partants).
    score += _num(cheval.get("forme")) * coef_forme
    score += _num(cheval.get("regularite")) * coef_regularite
    score += _num(cheval.get("gains")) * 2.5
    score += _num(cheval.get("jockey_score")) * coef_jockey
    score += _num(cheval.get("cote")) * coef_cote
    score += _num(cheval.get("distance")) * 2.5
    score += _num(cheval.get("terrain")) * 2.0
    score += _num(cheval.get("experience")) * coef_experience

    # --- 3. CRITÈRE OR AU TROT (ATTELÉ ET MONTÉ) : DÉFERRAGE (D4, DP, DA) ---
    # Utilise le code déjà normalisé par pmu_source.normaliser_deferrage() ;
    # reste tolérant aux anciennes valeurs textuelles si jamais fournies
    # directement (ex. tests, ou données saisies manuellement).
    if specialite in ("ATTELE", "MONTE"):
        deferrage = str(cheval.get("deferre", "") or "").strip().upper()
        if deferrage in ("D4", "DÉFERRÉ 4 PIEDS", "D4_4"):
            score += 18.0  # Gros bonus pour déferré des 4
        elif deferrage in ("DP", "DA", "DÉFERRÉ ANTÉRIEURS", "DÉFERRÉ POSTÉRIEURS"):
            score += 9.0   # Bonus modéré pour déferré 2 pieds

    # --- 4. CORDE / STALLE (PLAT UNIQUEMENT) ---
    if specialite == "PLAT":
        num_corde = cheval.get("corde")
        if isinstance(num_corde, (int, float)) and num_corde <= 4:
            score += 12.0  # Corde favorable (1 à 4)

    # --- 5. BONUS PERFORMANCES RÉCENTES (TOP 3) ---
    performances = cheval.get("performances", [])
    if performances:
        bonnes_places = 0
        for place in performances:
            if isinstance(place, (int, float)) and place <= 3:
                bonnes_places += 1
        score += bonnes_places * 6.0

    return round(score, 2)
