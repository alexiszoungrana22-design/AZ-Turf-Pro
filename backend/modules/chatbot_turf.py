"""AZ Turf Pro - Assistant Premium conversationnel."""
import re


def _num(v, default=0.0):
    try: return float(v)
    except (TypeError, ValueError): return default


def _horses(moteur):
    return moteur.get("classement") or moteur.get("chevaux") or []


def _horse(horses, n):
    return next((h for h in horses if str(h.get("numero")) == str(n)), None)


def _premium(tickets):
    return (tickets or {}).get("premium") or {}


def _fmt(items):
    out=[]
    for x in items or []:
        out.append(str(x.get("numero")) if isinstance(x,dict) else str(x))
    return " - ".join(out)


def _course(moteur):
    return moteur.get("lecture_course") or moteur.get("profil_course") or moteur.get("course") or moteur.get("info_course") or {}


def _horse_line(h):
    return (f"N°{h.get('numero')} {h.get('nom')} | AZ {h.get('indice_az')} | "
            f"Premium {h.get('indice_premium')} | cote {h.get('cote')}")


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q=(question or "").lower().strip()
    moteur=(contexte_analyse or {}).get("moteur") or {}
    horses=_horses(moteur)
    tickets=moteur.get("tickets") or {}
    premium=_premium(tickets)
    course=_course(moteur)

    # Comparaison: traiter avant "meilleur" pour ne pas tomber sur le favori.
    if any(k in q for k in ("compare", "comparaison", "versus", " vs ")):
        nums=re.findall(r"\b(?:n[°o]\s*)?(\d{1,2})\b", q)
        if len(nums)>=2:
            a,b=_horse(horses,nums[0]),_horse(horses,nums[1])
            if a and b:
                pa=_num(a.get("indice_premium")); pb=_num(b.get("indice_premium"))
                winner=a if pa>=pb else b
                return {"status":"success","question":question,"reponse":
                    f"⚔️ **Comparaison Premium**\n\n• {_horse_line(a)}\n• {_horse_line(b)}\n\n🏆 Avantage Premium : **N°{winner.get('numero')} {winner.get('nom')}**.\n"
                    "La décision tient compte de l'indice Premium disponible, pas seulement de la musique."}

    # Outsider: chercher parmi les cotes hautes, puis choisir le meilleur indice Premium.
    if any(k in q for k in ("outsider","tocard","surprise","pépite","pepite","value")):
        candidates=[h for h in horses if _num(h.get("cote"))>=8 and not h.get("est_non_partant")]
        candidates.sort(key=lambda h:_num(h.get("indice_premium")), reverse=True)
        if candidates:
            h=candidates[0]
            return {"status":"success","question":question,"reponse":
                f"🔥 **Meilleur outsider Premium : N°{h.get('numero')} {h.get('nom')}**\n"
                f"Cote : **{h.get('cote')}** | Indice Premium : **{h.get('indice_premium')}**\n\n"
                "Il est classé outsider ici parce que sa cote est élevée tout en conservant un profil Premium compétitif."}
        return {"status":"success","question":question,"reponse":"Aucun outsider suffisamment documenté n'est disponible."}

    # Analyse course: lire exactement lecture_course créée par engine.py.
    if any(k in q for k in ("analyse la course","analyse course","lecture de course","scénario","scenario")):
        lc=course if isinstance(course,dict) else {}
        profil=lc.get("profil") or lc.get("profil_course") or {}
        if isinstance(profil,dict):
            lines=["🧠 **Lecture de course Premium**"]
            for key,label in (("discipline","Discipline"),("distance","Distance"),("type_depart","Type de départ"),("partants","Partants")):
                val=profil.get(key)
                if val not in (None,"",0): lines.append(f"- {label} : {val}")
            lecture=profil.get("lecture")
            if lecture: lines.append("- Lecture : " + " ; ".join(map(str,lecture)))
            if profil.get("confiance") is not None: lines.append(f"- Confiance : {profil.get('confiance')}")
            forts=lc.get("points_forts") or []
            risques=lc.get("points_attention") or []
            if forts: lines += ["", "✅ **Points favorables :** " + " ; ".join(forts)]
            if risques: lines += ["", "⚠️ **Points d'attention :** " + " ; ".join(risques)]
            return {"status":"success","question":question,"reponse":"\n".join(lines)}

    # Ticket Premium: structure réelle de quinte.py.
    if any(k in q for k in ("quinté","quinte","ticket","combinaison","sélection premium","selection premium")):
        lines=["🎟️ **Ticket Premium AZ Turf Pro**"]
        if premium.get("quinte"): lines.append(f"Quinté : **{_fmt(premium['quinte'])}**")
        if premium.get("selection_quinte"): lines.append(f"Sélection Premium : **{_fmt(premium['selection_quinte'])}**")
        if premium.get("quarte"): lines.append(f"Quarté : **{_fmt(premium['quarte'])}**")
        if premium.get("trio"): lines.append(f"Trio : **{_fmt(premium['trio'])}**")
        if premium.get("champ_reduit"): lines.append(f"Champ réduit : **{premium['champ_reduit']}")
        if len(lines)>1: return {"status":"success","question":question,"reponse":"\n".join(lines)}
        return {"status":"success","question":question,"reponse":"Le ticket Premium n'est pas disponible dans les données actuelles."}

    # Cheval précis.
    m=re.search(r"\b(?:n[°o]\s*)?(\d{1,2})\b",q)
    if m and any(k in q for k in ("cheval","pourquoi","explique","analyse","avis","profil")):
        h=_horse(horses,m.group(1))
        if h: return {"status":"success","question":question,"reponse":f"🐎 **Profil du N°{h.get('numero')} {h.get('nom')}**\n{_horse_line(h)}"}

    # Favori/base: après les intents spécifiques.
    if any(k in q for k in ("meilleure base","meilleur cheval","favori","coup sûr","coup sur","gagnant","top")):
        if horses:
            top=max(horses,key=lambda h:_num(h.get("indice_premium")))
            return {"status":"success","question":question,"reponse":
                f"🎯 **Base Premium : N°{top.get('numero')} {top.get('nom')}**\n"
                f"Indice AZ : **{top.get('indice_az')}** | Indice Premium : **{top.get('indice_premium')}**"}
        return {"status":"success","question":question,"reponse":"Veuillez lancer l'analyse de la course."}

    if "badge" in q or "signification" in q:
        return {"status":"success","question":question,"reponse":
            "🏷️ **Badges AZ Turf Pro**\n- D4 : déferré des 4 pieds.\n- Duo Chaud 🔥 : signal lié à l'entourage.\n- Spécialiste 🎯 : aptitude détectée.\n- Rachat ⚡ : profil à reconsidérer après une contre-performance."}

    if any(k in q for k in ("favoris vulnérables","favori vulnérable","favoris à éviter","piège","piege")):
        if horses:
            ordered=sorted(horses,key=lambda h:_num(h.get("indice_premium")))[:3]
            return {"status":"success","question":question,"reponse":"⚠️ **Profils Premium à examiner avec prudence :** " + ", ".join(f"N°{h.get('numero')} {h.get('nom')}" for h in ordered)}

    return {"status":"success","question":question,"reponse":
        "🤖 Je peux analyser la course, le ticket Premium, un cheval, comparer deux chevaux, chercher un outsider, repérer des favoris vulnérables et expliquer les badges."}
