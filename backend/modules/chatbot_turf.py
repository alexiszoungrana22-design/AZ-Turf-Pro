"""
AZ TURF PRO - ASSISTANT CONVERSATIONNEL IA

Le chatbot utilise les données réellement produites par le moteur.
Pour les questions de ticket, le Premium est prioritaire.
"""

import re


def _nombre(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _cheval(classement, numero):
    for c in classement or []:
        if str(c.get("numero")) == str(numero):
            return c
    return None


def _ticket_premium(tickets):
    tickets = tickets or {}
    return tickets.get("premium") or {}


def _nums(items):
    return " - ".join(
        str(x.get("numero")) if isinstance(x, dict) else str(x)
        for x in (items or [])
    )


def _lecture_premium(premium):
    return premium.get("lecture_course") or {}


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = (question or "").lower().strip()
    moteur = (contexte_analyse or {}).get("moteur", {})
    classement = moteur.get("classement", []) or []
    tickets = moteur.get("tickets", {}) or {}
    premium = _ticket_premium(tickets)
    lecture = _lecture_premium(premium)

    # Analyse de la course
    if any(x in q for x in (
        "analyse la course", "analyse course", "lecture de course",
        "scénario", "scenario", "parcours"
    )):
        profil = lecture.get("profil", {})
        forts = lecture.get("points_forts", [])
        attention = lecture.get("points_attention", [])

        lignes = ["🧠 **Lecture de course Premium**"]
        if profil:
            for cle, valeur in profil.items():
                if valeur not in (None, "", [], {}):
                    lignes.append(f"- {cle.replace('_', ' ').capitalize()} : {valeur}")
        if forts:
            lignes.append("\n✅ **Points favorables :** " + " ; ".join(map(str, forts)))
        if attention:
            lignes.append("\n⚠️ **Points d'attention :** " + " ; ".join(map(str, attention)))

        if len(lignes) == 1:
            lignes.append("La lecture contextuelle Premium n'a pas encore assez de données pour détailler cette course.")

        return {"status": "success", "question": question, "reponse": "\n".join(lignes)}

    # Ticket Premium : jamais le gratuit
    if any(x in q for x in ("quinté", "quinte", "ticket premium", "ticket", "combinaison", "sélection premium", "selection premium")):
        quinte = premium.get("quinte", [])
        selection = premium.get("selection_quinte", [])
        quarte = premium.get("quarte", [])
        trio = premium.get("trio", [])
        champ = premium.get("champ_reduit", {})

        lignes = ["🎟️ **Ticket Premium AZ Turf Pro**"]
        if quinte:
            lignes.append(f"Quinté : **{_nums(quinte)}**")
        if selection:
            lignes.append(f"Sélection Premium : **{_nums(selection)}**")
        if quarte:
            lignes.append(f"Quarté : **{_nums(quarte)}**")
        if trio:
            lignes.append(f"Trio : **{_nums(trio)}**")
        if isinstance(champ, dict) and champ.get("format"):
            lignes.append(f"Champ réduit : **{champ['format']}**")
        elif champ:
            lignes.append(f"Champ réduit : **{champ}**")

        if len(lignes) == 1:
            lignes.append("Le ticket Premium n'est pas encore disponible pour cette analyse.")

        return {"status": "success", "question": question, "reponse": "\n".join(lignes)}

    # Comparaison
    nums = re.findall(r"\b(\d{1,2})\b", q)
    if any(x in q for x in ("compare", "comparaison", "versus", " vs ")) and len(nums) >= 2:
        a, b = _cheval(classement, nums[0]), _cheval(classement, nums[1])
        if a and b:
            sa = _nombre(a.get("indice_premium"))
            sb = _nombre(b.get("indice_premium"))
            meilleur = a if sa >= sb else b
            return {
                "status": "success",
                "question": question,
                "reponse": (
                    f"⚔️ **N°{a.get('numero')} {a.get('nom')} vs N°{b.get('numero')} {b.get('nom')}**\n"
                    f"- N°{a.get('numero')} : Indice Premium {a.get('indice_premium')}\n"
                    f"- N°{b.get('numero')} : Indice Premium {b.get('indice_premium')}\n\n"
                    f"Avantage Premium : **N°{meilleur.get('numero')} {meilleur.get('nom')}**."
                ),
            }

    # Cheval précis
    match = re.search(r"\b(?:n[°o]\s*)?(\d{1,2})\b", q)
    if match and any(x in q for x in ("cheval", "pourquoi", "explique", "analyse", "profil", "avis")):
        c = _cheval(classement, match.group(1))
        if c:
            details = [
                f"🐎 **N°{c.get('numero')} {c.get('nom')}**",
                f"Indice AZ : **{c.get('indice_az')}**",
                f"Indice Premium : **{c.get('indice_premium')}**",
            ]
            if c.get("cote") not in (None, "", 0):
                details.append(f"Cote : **{c.get('cote')}**")
            return {"status": "success", "question": question, "reponse": "\n".join(details)}

    # Outsider
    if any(x in q for x in ("outsider", "tocard", "surprise", "pépite", "pepite", "value")):
        candidats = [c for c in classement if _nombre(c.get("cote")) >= 8]
        candidats.sort(key=lambda c: _nombre(c.get("indice_premium")), reverse=True)
        if candidats:
            c = candidats[0]
            return {
                "status": "success",
                "question": question,
                "reponse": (
                    f"🔥 **Outsider Premium : N°{c.get('numero')} {c.get('nom')}**\n"
                    f"Cote : **{c.get('cote')}** | Indice Premium : **{c.get('indice_premium')}**"
                ),
            }
        return {"status": "success", "question": question, "reponse": "Aucun outsider suffisamment documenté n'est identifié."}

    # Favoris vulnérables
    if any(x in q for x in ("favoris vulnérables", "favori vulnérable", "favoris à éviter", "piège", "piege")):
        if classement:
            faibles = sorted(classement, key=lambda c: _nombre(c.get("indice_premium")))[:3]
            return {
                "status": "success",
                "question": question,
                "reponse": "⚠️ **À examiner avec prudence :** " + ", ".join(
                    f"N°{c.get('numero')} {c.get('nom')}" for c in faibles
                ),
            }

    # Favori/base
    if any(x in q for x in ("favori", "coup sur", "coup sûr", "meilleur", "gagnant", "base")):
        if classement:
            c = classement[0]
            return {
                "status": "success",
                "question": question,
                "reponse": (
                    f"🎯 **Base AZ Turf Pro : N°{c.get('numero')} {c.get('nom')}**\n"
                    f"Indice AZ : **{c.get('indice_az')}** | Indice Premium : **{c.get('indice_premium')}**"
                ),
            }
        return {"status": "success", "question": question, "reponse": "Lancez d'abord une analyse de course."}

    # Badges
    if "badge" in q or "signification" in q:
        return {
            "status": "success",
            "question": question,
            "reponse": (
                "🏷️ **Badges AZ Turf Pro**\n"
                "- D4 : déferré des 4 pieds.\n"
                "- Duo Chaud 🔥 : signal lié à l'entourage.\n"
                "- Spécialiste 🎯 : aptitude détectée.\n"
                "- Rachat ⚡ : profil à reconsidérer après une contre-performance."
            ),
        }

    return {
        "status": "success",
        "question": question,
        "reponse": (
            "🤖 **Assistant AZ Turf Pro**\n\n"
            "Je peux analyser la course, le ticket Premium, un cheval précis, "
            "deux chevaux en comparaison, les outsiders, les favoris vulnérables "
            "et les badges."
        ),
    }
