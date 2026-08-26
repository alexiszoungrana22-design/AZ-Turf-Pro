"""AZ Turf Pro - Assistant Premium conversationnel.

Cette couche interprète le contexte déjà produit par le moteur Premium.
Elle n'altère ni le scoring gratuit ni la génération des tickets.
"""
import re


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _horses(moteur):
    horses = moteur.get("classement") or moteur.get("chevaux") or []
    return [h for h in horses if isinstance(h, dict) and not h.get("est_non_partant")]


def _horse(horses, number):
    return next((h for h in horses if str(h.get("numero")) == str(number)), None)


def _premium(tickets):
    return (tickets or {}).get("premium") or {}


def _fmt(items):
    return " - ".join(str(x.get("numero")) if isinstance(x, dict) else str(x) for x in (items or []))


def _course(moteur):
    """Fusionne la lecture Premium avec le contexte brut de course."""
    lecture = moteur.get("lecture_course") or _premium(moteur.get("tickets")).get("lecture_course") or {}
    raw = moteur.get("course") or moteur.get("info_course") or {}
    if not isinstance(lecture, dict): lecture = {}
    if not isinstance(raw, dict): raw = {}
    merged = dict(raw)
    merged.update(lecture)
    profil = lecture.get("profil")
    if isinstance(profil, dict):
        raw_profile = raw.get("profil_course") or raw.get("profil") or {}
        merged["profil"] = {**raw_profile, **profil} if isinstance(raw_profile, dict) else dict(profil)
    return merged


def _profile(course):
    if not isinstance(course, dict):
        return {}
    return course.get("profil") if isinstance(course.get("profil"), dict) else course


def _horse_line(h):
    parts = [f"N°{h.get('numero')} {h.get('nom')}"]
    if h.get("indice_az") is not None:
        parts.append(f"AZ {h.get('indice_az')}")
    if h.get("indice_premium") is not None:
        parts.append(f"Premium {h.get('indice_premium')}")
    if h.get("cote") not in (None, "", 0):
        parts.append(f"cote {h.get('cote')}")
    return " | ".join(parts)


def _premium_score(h):
    return _num(h.get("indice_premium"), _num(h.get("premium_score"), 0))


def _top_two(horses):
    return sorted(horses, key=_premium_score, reverse=True)[:2]


def _outsider_score(h):
    """Score d'intérêt outsider : potentiel Premium + prix, sans confondre outsider et simple favori."""
    cote = _num(h.get("cote"), 0)
    premium = _premium_score(h)
    if cote < 8:
        return -1e9
    # Le prix augmente l'intérêt, mais ne peut pas compenser totalement un profil Premium faible.
    return premium + min(cote, 30) * 1.5


def _horse_context(course, numero):
    if not isinstance(course, dict):
        return {}
    contexts = course.get("chevaux")
    if isinstance(contexts, dict):
        return contexts.get(str(numero), {}) or {}
    return {}


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = (question or "").lower().strip()
    moteur = (contexte_analyse or {}).get("moteur") or {}
    horses = _horses(moteur)
    tickets = moteur.get("tickets") or {}
    premium = _premium(tickets)
    course = _course(moteur)
    profile = _profile(course)

    # Comparaison explicite : priorité à cette intention, même si la question contient "meilleur".
    if any(k in q for k in ("compare", "comparaison", "versus", " vs ")):
        nums = re.findall(r"\b(?:n[°o]\s*)?(\d{1,2})\b", q)
        pair = None
        if len(nums) >= 2:
            a, b = _horse(horses, nums[0]), _horse(horses, nums[1])
            if a and b:
                pair = (a, b)
        if pair is None and any(k in q for k in ("deux meilleurs", "2 meilleurs", "deux top", "top 2")):
            best = _top_two(horses)
            if len(best) == 2:
                pair = (best[0], best[1])
        if pair:
            a, b = pair
            pa, pb = _premium_score(a), _premium_score(b)
            winner = a if pa >= pb else b
            lines = ["⚔️ **Comparaison Premium**", "", f"• {_horse_line(a)}", f"• {_horse_line(b)}", "",
                     f"🏆 Avantage Indice Premium : **N°{winner.get('numero')} {winner.get('nom')}**."]
            ca, cb = _horse_context(course, a.get("numero")), _horse_context(course, b.get("numero"))
            if ca.get("raisons"): lines.append(f"N°{a.get('numero')} — points forts : " + " ; ".join(ca["raisons"][:3]))
            if cb.get("raisons"): lines.append(f"N°{b.get('numero')} — points forts : " + " ; ".join(cb["raisons"][:3]))
            if ca.get("risques"): lines.append(f"N°{a.get('numero')} — attention : " + " ; ".join(ca["risques"][:2]))
            if cb.get("risques"): lines.append(f"N°{b.get('numero')} — attention : " + " ; ".join(cb["risques"][:2]))
            return {"status":"success","question":question,"reponse":"\n".join(lines)}

    # Outsider : uniquement cote >= 8, avec diversification par rapport aux deux meilleurs Premium.
    if any(k in q for k in ("outsider", "tocard", "surprise", "pépite", "pepite", "value")):
        top_nums = {str(h.get("numero")) for h in _top_two(horses)}
        candidates = [h for h in horses if _num(h.get("cote")) >= 8]
        candidates.sort(key=_outsider_score, reverse=True)
        if candidates:
            # Si possible, préférer un vrai outsider hors top 2 pour ne pas confondre base et outsider.
            outside = [h for h in candidates if str(h.get("numero")) not in top_nums]
            h = (outside or candidates)[0]
            ctx = _horse_context(course, h.get("numero"))
            lines = [f"🔥 **Meilleur outsider Premium : N°{h.get('numero')} {h.get('nom')}**",
                     f"Cote : **{h.get('cote')}** | Indice Premium : **{h.get('indice_premium')}**"]
            if ctx.get("raisons"): lines.append("Points forts : " + " ; ".join(ctx["raisons"][:3]))
            if ctx.get("risques"): lines.append("Points d'attention : " + " ; ".join(ctx["risques"][:2]))
            lines.append("Ce choix est séparé des bases : il combine prix élevé et profil Premium compétitif.")
            return {"status":"success","question":question,"reponse":"\n".join(lines)}
        return {"status":"success","question":question,"reponse":"Aucun outsider suffisamment documenté n'est disponible."}

    # Lecture de course Premium : priorité à tickets.premium.lecture_course.
    if any(k in q for k in ("analyse la course", "analyse course", "lecture de course", "scénario", "scenario")):
        if isinstance(profile, dict) and profile:
            lines = ["🧠 **Lecture de course Premium**"]
            for key, label in (("discipline","Discipline"),("distance","Distance"),("type_depart","Type de départ"),("partants","Partants")):
                val = profile.get(key)
                if val not in (None, "", 0): lines.append(f"- {label} : {val}")
            lecture = profile.get("lecture")
            if lecture:
                lines.append("- Lecture : " + " ; ".join(map(str, lecture)) if isinstance(lecture, list) else f"- Lecture : {lecture}")
            if profile.get("confiance") is not None: lines.append(f"- Confiance : {profile.get('confiance')}")
            forts = course.get("points_forts") or []
            risques = course.get("points_attention") or []
            if forts: lines += ["", "✅ **Points favorables :** " + " ; ".join(map(str, forts))]
            if risques: lines += ["", "⚠️ **Points d'attention :** " + " ; ".join(map(str, risques))]
            methode = course.get("methode")
            if methode: lines += ["", "🔎 " + str(methode)]
            return {"status":"success","question":question,"reponse":"\n".join(lines)}
        return {"status":"success","question":question,"reponse":"La lecture contextuelle Premium n'est pas disponible dans le contexte transmis."}

    # Ticket Premium : champs exacts de quinte.py.
    if any(k in q for k in ("quinté", "quinte", "ticket", "combinaison", "sélection premium", "selection premium")):
        lines = ["🎟️ **Ticket Premium AZ Turf Pro**"]
        if premium.get("quinte"): lines.append(f"Quinté : **{_fmt(premium['quinte'])}**")
        if premium.get("selection_quinte"): lines.append(f"Sélection Premium : **{_fmt(premium['selection_quinte'])}**")
        if premium.get("quarte"): lines.append(f"Quarté : **{_fmt(premium['quarte'])}**")
        if premium.get("trio"): lines.append(f"Trio : **{_fmt(premium['trio'])}**")
        champ = premium.get("champ_reduit")
        if isinstance(champ, dict): champ = champ.get("format")
        if champ: lines.append(f"Champ réduit : **{champ}**")
        if premium.get("methode"): lines.append(f"Méthode : {premium['methode']}")
        if len(lines) > 1: return {"status":"success","question":question,"reponse":"\n".join(lines)}
        return {"status":"success","question":question,"reponse":"Le ticket Premium n'est pas disponible dans les données actuelles."}

    # Cheval précis.
    m = re.search(r"\b(?:n[°o]\s*)?(\d{1,2})\b", q)
    if m and any(k in q for k in ("cheval", "pourquoi", "explique", "analyse", "avis", "profil")):
        h = _horse(horses, m.group(1))
        if h:
            ctx = _horse_context(course, h.get("numero"))
            lines = [f"🐎 **Profil du N°{h.get('numero')} {h.get('nom')}**", _horse_line(h)]
            if ctx.get("raisons"): lines.append("Points forts : " + " ; ".join(ctx["raisons"][:4]))
            if ctx.get("risques"): lines.append("Points d'attention : " + " ; ".join(ctx["risques"][:3]))
            return {"status":"success","question":question,"reponse":"\n".join(lines)}

    # Favoris vulnérables : traiter avant l'intention générique "favori".
    if (("favoris" in q or "favori" in q) and ("vulnérable" in q or "eviter" in q or "éviter" in q)) or "piège" in q or "piege" in q:
        if horses:
            ordered = sorted(horses, key=_premium_score)[:3]
            return {"status":"success","question":question,"reponse":"⚠️ **Profils Premium à examiner avec prudence :** " + ", ".join(f"N°{h.get('numero')} {h.get('nom')}" for h in ordered)}

    # Base/favori : après les intentions spécifiques.
    if any(k in q for k in ("meilleure base", "meilleur cheval", "favori", "coup sûr", "coup sur", "gagnant", "top")):
        if horses:
            top = max(horses, key=_premium_score)
            return {"status":"success","question":question,"reponse":
                f"🎯 **Base Premium : N°{top.get('numero')} {top.get('nom')}**\n"
                f"Indice AZ : **{top.get('indice_az')}** | Indice Premium : **{top.get('indice_premium')}**\n"
                "La base repose sur la solidité Premium et doit être distinguée de l'outsider."}
        return {"status":"success","question":question,"reponse":"Veuillez lancer l'analyse de la course."}

    if "badge" in q or "signification" in q:
        return {"status":"success","question":question,"reponse":
            "🏷️ **Badges AZ Turf Pro**\n- D4 : déferré des 4 pieds.\n- Duo Chaud 🔥 : signal lié à l'entourage.\n- Spécialiste 🎯 : aptitude détectée.\n- Rachat ⚡ : profil à reconsidérer après une contre-performance."}

    return {"status":"success","question":question,"reponse":
        "🤖 Je peux analyser la course, le ticket Premium, un cheval, comparer deux chevaux, chercher un outsider, repérer des favoris vulnérables et expliquer les badges."}
