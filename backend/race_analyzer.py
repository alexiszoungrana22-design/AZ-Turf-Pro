"""
AZ TURF PRO - LECTURE CONTEXTUELLE PREMIUM

Couche additive : elle ne remplace aucun calcul historique.
Elle sert uniquement a enrichir l'Indice Premium avec le contexte de la course.
"""


def _float(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _text(value):
    return str(value or "").strip().upper()


def _first(d, keys, default=None):
    if not isinstance(d, dict):
        return default
    for key in keys:
        value = d.get(key)
        if value not in (None, "", []):
            return value
    return default


def _distance(course):
    return _float(_first(course, ("distance_course", "distance", "distanceCourse", "distanceMetres"), 0), 0)


def _start_type(course):
    return _text(_first(course, ("type_depart", "typeDepart", "mode_depart", "modeDepart", "depart"), ""))


def _is_autostart(course):
    return "AUTO" in _start_type(course)


def _race_profile(course, horses):
    distance = _distance(course)
    discipline = _text(course.get("discipline", ""))
    start_type = _start_type(course)
    runners = len([h for h in horses if isinstance(h, dict)])

    profile = []
    confidence = 0.45

    if distance:
        if distance <= 1600:
            profile.append("course de vitesse")
        elif distance <= 2200:
            profile.append("distance intermédiaire")
        elif distance <= 2700:
            profile.append("distance de tenue")
        else:
            profile.append("course d'endurance")
        confidence += 0.10

    if _is_autostart(course):
        profile.append("départ autostart : la mise en jambes et le placement comptent davantage")
        confidence += 0.20
    elif start_type:
        profile.append("départ : " + start_type.lower())
        confidence += 0.10

    if runners:
        profile.append(f"peloton de {runners} partants")

    if not profile:
        profile.append("profil de course partiellement documenté")

    return {
        "discipline": discipline or "NON DOCUMENTÉE",
        "distance": distance,
        "type_depart": start_type or "NON DOCUMENTÉ",
        "partants": runners,
        "lecture": profile,
        "confiance": round(min(1.0, confidence), 2),
    }


def _horse_context(horse, course, profile):
    score = 0.0
    reasons = []
    risks = []

    distance = profile["distance"]
    pref = _float(_first(horse, ("distance_predilection", "distance_pref", "distance_prefered"), 0), 0)
    if distance and pref:
        ecart = abs(distance - pref)
        if ecart <= 100:
            score += 9.0
            reasons.append("distance très proche de sa préférence")
        elif ecart <= 250:
            score += 5.0
        elif ecart >= 600:
            score -= 5.0
            risks.append("distance éloignée de sa préférence déclarée")

    # Le numéro n'est interprété que lorsque la configuration du départ est connue.
    numero = int(_float(horse.get("numero", 0), 0))
    if numero and _is_autostart(course):
        if numero in (2, 3, 4, 5):
            score += 5.0
            reasons.append("numéro favorable au placement à l'autostart")
        elif numero in (1, 8, 9, 10, 11, 16):
            score -= 4.0
            risks.append("numéro potentiellement piégeux à l'autostart")

    forme = _float(horse.get("forme", 0), 0)
    regularite = _float(horse.get("regularite", 0), 0)
    if forme >= 7:
        score += 4.0
        reasons.append("forme récente suffisamment solide")
    if regularite >= 7:
        score += 3.0
        reasons.append("profil régulier")

    # Déferrage : signal d'entourage, mais jamais preuve d'objectif à lui seul.
    deferre = _text(horse.get("deferre", ""))
    if deferre in ("D4", "DÉFERRÉ 4 PIEDS", "D4_4"):
        score += 5.0
        reasons.append("configuration déferrée forte : signal d'entourage")
    elif deferre in ("DP", "DA", "DP_DG", "DÉFERRÉ ANTÉRIEURS", "DÉFERRÉ POSTÉRIEURS"):
        score += 2.5
        reasons.append("déferrage : signal positif mais modéré")

    # Engagement : uniquement si les données existent réellement.
    engagement = _first(horse, ("engagement_score", "engagement", "engagement_qualite"), None)
    if engagement is not None:
        engagement_value = _float(engagement, 0)
        score += max(-8.0, min(10.0, (engagement_value - 50.0) * 0.20))
        if engagement_value >= 75:
            reasons.append("engagement signalé comme particulièrement favorable")
        elif engagement_value <= 35:
            risks.append("engagement signalé comme délicat")

    # Catégorie : si la source fournit explicitement le changement, on l'utilise.
    if horse.get("hausse_de_categorie") is True:
        score -= 7.0
        risks.append("hausse de catégorie")
    elif horse.get("baisse_de_categorie") is True:
        score += 6.0
        reasons.append("retour dans une catégorie plus favorable")

    # Marché : utilisé comme information de contexte, jamais comme preuve de forme.
    cote = _float(horse.get("cote", 0), 0)
    variation = _float(horse.get("variation_cote_pct", 0), 0)
    if variation <= -15:
        score += 3.0
        reasons.append("cote en baisse : soutien du marché à surveiller")
    elif variation >= 20:
        score -= 2.0
        risks.append("cote en hausse : marché moins favorable")

    # Entourage : on ne prétend pas mesurer sa qualité sans statistiques.
    if horse.get("jockey") and horse.get("entraineur"):
        reasons.append("couple jockey/entraîneur identifié dans les données")

    # Une cote très basse n'est pas transformée automatiquement en bonus.
    if cote and cote <= 3:
        risks.append("favori de marché : risque de valeur faible si la cote est écrasée")

    return {
        "bonus": round(score, 2),
        "raisons": reasons[:6],
        "risques": risks[:5],
    }


def analyser_course_premium(course, horses):
    """Analyse la course et fournit uniquement des signaux destinés au Premium."""
    course = course if isinstance(course, dict) else {}
    horses = horses if isinstance(horses, list) else []

    profile = _race_profile(course, horses)
    contexts = {}
    for horse in horses:
        if not isinstance(horse, dict):
            continue
        numero = str(horse.get("numero", ""))
        contexts[numero] = _horse_context(horse, course, profile)

    # Lecture synthétique : elle reste prudente si les données structurelles manquent.
    all_reasons = []
    all_risks = []
    for context in contexts.values():
        all_reasons.extend(context["raisons"])
        all_risks.extend(context["risques"])

    def top_unique(items, limit):
        out = []
        seen = set()
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
            if len(out) >= limit:
                break
        return out

    return {
        "profil_course": profile,
        "signaux": {
            "points_forts": top_unique(all_reasons, 5),
            "points_attention": top_unique(all_risks, 5),
        },
        "chevaux": contexts,
    }


def bonus_premium_cheval(analysis, cheval):
    """Retourne uniquement le bonus contextuel à intégrer à l'Indice Premium."""
    if not isinstance(analysis, dict) or not isinstance(cheval, dict):
        return 0.0
    numero = str(cheval.get("numero", ""))
    context = (analysis.get("chevaux") or {}).get(numero) or {}
    return _float(context.get("bonus", 0), 0)
