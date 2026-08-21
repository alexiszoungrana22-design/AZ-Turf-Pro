"""
AZ TURF PRO - ASSISTANT CONVERSATIONNEL IA
Moteur autonome PMU : conversation, analyse indépendante, tickets,
recherche de courses, mémoire et explications.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import math
import re
from typing import Any


PMU_KNOWLEDGE = {
    "quinte": "Le Quinté+ est un pari combiné consistant à trouver les cinq premiers chevaux de la course dans l'ordre ou dans certaines formules selon le type de pari choisi.",
    "tierce": "Le Tiercé consiste à trouver les trois premiers chevaux, avec une formule dans l'ordre ou désordre selon le pari.",
    "quarte": "Le Quarté consiste à sélectionner les quatre premiers chevaux, avec différentes formules selon le pari choisi.",
    "couple": "Le Couplé consiste à associer deux chevaux pour viser les deux premières places selon la formule Gagnant ou Placé.",
    "simple": "Le Simple permet de jouer un cheval pour la victoire (Gagnant) ou pour une place parmi les chevaux classés (Placé), selon les règles du pari.",
    "outsider": "Un outsider est un cheval dont la cote est relativement élevée mais dont le profil présente suffisamment d'arguments pour envisager une surprise.",
    "tocard": "Un tocard est généralement un cheval très délaissé au marché, mais susceptible de créer une grosse surprise.",
    "cote": "La cote reflète le niveau de confiance implicite du marché. L'assistant la compare à sa propre estimation pour rechercher de la value.",
    "d4": "D4 signifie déferré des quatre pieds dans le trot. C'est une information d'équipement qui peut être importante, mais elle ne suffit jamais à elle seule pour sélectionner un cheval.",
    "musique": "La musique résume les dernières performances du cheval. Elle doit être interprétée avec le contexte : niveau des courses, discipline, distance et conditions.",
}


def _num(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _positions(cheval: dict) -> list[int]:
    raw = cheval.get("performances") or cheval.get("musique_brute") or []
    if isinstance(raw, list):
        return [int(x) for x in raw if str(x).isdigit() and int(x) > 0]
    return [int(x) for x in re.findall(r"\d+", str(raw)) if int(x) > 0]


def _score_forme(c: dict) -> float:
    positions = _positions(c)
    if positions:
        recent = positions[:5]
        return max(0.0, min(10.0, 10.5 - sum(recent) / len(recent)))
    return _num(c.get("forme"), 5.0)


def _score_reg(c: dict) -> float:
    positions = _positions(c)
    if len(positions) >= 2:
        vals = positions[:8]
        avg = sum(vals) / len(vals)
        sd = math.sqrt(sum((x - avg) ** 2 for x in vals) / len(vals))
        return max(0.0, min(10.0, 10.0 - sd))
    return _num(c.get("regularite"), 5.0)


def _score_cote(c: dict, all_c: list[dict]) -> float:
    cote = _num(c.get("cote_brute", c.get("cote")), 0)
    vals = [_num(x.get("cote_brute", x.get("cote")), 0) for x in all_c]
    vals = [x for x in vals if x > 0]
    if not cote or not vals or max(vals) == min(vals):
        return 5.0
    # Une cote basse augmente la probabilité brute, mais ne domine pas le modèle.
    return max(0.0, min(10.0, (max(vals) - cote) / (max(vals) - min(vals)) * 10))


def score_independant(cheval: dict, tous: list[dict]) -> dict:
    """Score indépendant du classement AZ. Les pondérations sont explicites."""
    forme = _score_forme(cheval)
    regularite = _score_reg(cheval)
    cote_score = _score_cote(cheval, tous)
    gains = _num(cheval.get("gains_carriere_brute"), 0)
    gains_vals = [_num(x.get("gains_carriere_brute"), 0) for x in tous]
    gains_vals = [x for x in gains_vals if x >= 0]
    gains_score = 5.0 if not gains_vals or max(gains_vals) == min(gains_vals) else (gains - min(gains_vals)) / (max(gains_vals) - min(gains_vals)) * 10
    experience = max(0.0, min(10.0, _num(cheval.get("experience"), 5)))
    aptitude = max(0.0, min(10.0, _num(cheval.get("distance"), 5) * 0.6 + _num(cheval.get("terrain"), 5) * 0.4))
    jockey = max(0.0, min(10.0, _num(cheval.get("jockey_score"), 5)))

    score = (
        forme * 0.22 +
        regularite * 0.14 +
        aptitude * 0.14 +
        jockey * 0.10 +
        gains_score * 0.08 +
        experience * 0.07 +
        cote_score * 0.15 +
        max(0.0, min(10.0, (10.0 - _num(cheval.get("rang"), 10) / max(1, len(tous)) * 10))) * 0.10
    )
    return {
        "score_ia": round(score, 2),
        "forme": round(forme, 2),
        "regularite": round(regularite, 2),
        "aptitude": round(aptitude, 2),
        "cote_score": round(cote_score, 2),
        "gains": round(gains_score, 2),
        "experience": round(experience, 2),
        "jockey": round(jockey, 2),
    }


def construire_ticket_ia(classement: list[dict], style: str = "equilibre") -> dict:
    if not classement:
        return {"selection": [], "base": None, "outsiders": [], "details": []}

    scored = []
    for c in classement:
        s = score_independant(c, classement)
        item = {**c, **s}
        scored.append(item)

    if style == "speculatif":
        scored.sort(key=lambda x: (x["score_ia"] + min(_num(x.get("cote_brute", x.get("cote")), 0) / 10, 5)), reverse=True)
    elif style == "prudent":
        scored.sort(key=lambda x: x["score_ia"], reverse=True)
    elif style == "value":
        scored.sort(key=lambda x: x["score_ia"] - _num(x.get("cote_brute", x.get("cote")), 0) * 0.08, reverse=True)
    else:
        scored.sort(key=lambda x: x["score_ia"], reverse=True)

    selection = scored[:5]
    outsiders = [x for x in scored if _num(x.get("cote_brute", x.get("cote")), 0) >= 10][:3]
    base = scored[0]
    details = []
    for x in selection:
        details.append(
            f"N°{x.get('numero')} {x.get('nom')} — score IA {x['score_ia']}/10, forme {x['forme']}/10, régularité {x['regularite']}/10, aptitude {x['aptitude']}/10, cote {x.get('cote_brute', x.get('cote', 'N/D'))}."
        )
    return {"selection": selection, "base": base, "outsiders": outsiders, "details": details}


def _salutation(q: str, prenom: str = "") -> str | None:
    salutations = ("bonjour", "bonsoir", "salut", "hello", "coucou", "bon matin")
    if not any(q.startswith(x) or q == x for x in salutations):
        return None
    nom = f" {prenom}" if prenom else ""
    return f"🤖 Bonjour{nom} 👋 Comment allez-vous aujourd'hui ?\n\nJe suis l'Assistant Chatbot AZ Turf Pro. Sur quoi souhaitez-vous qu'on travaille aujourd'hui ? 🏇"


def _conversation(q: str) -> str | None:
    if any(x in q for x in ["je vais bien", "ça va", "ca va", "je vais très bien", "merci ça va", "merci"]):
        return "😊 Très bien, merci ! Sur quoi souhaitez-vous qu'on travaille aujourd'hui ? Je peux analyser une course, chercher une course à venir, construire un ticket IA, comparer avec AZ Turf Pro ou répondre à une question PMU."
    if q in {"d'accord", "ok", "okay", "oui", "oui oui", "très bien", "parfait"}:
        return "👍 Parfait. Que souhaitez-vous faire maintenant : analyser une course, préparer un ticket, chercher une course à venir ou revenir sur une course passée ?"
    return None


def _knowledge(q: str) -> str | None:
    keys = [
        ("quinté", "quinte"), ("tiercé", "tierce"), ("quarté", "quarte"),
        ("couplé", "couple"), ("simple", "simple"), ("outsider", "outsider"),
        ("tocard", "tocard"), ("cote", "cote"), ("d4", "d4"), ("musique", "musique"),
    ]
    for trigger, key in keys:
        if trigger in q:
            return f"📘 **PMU — {trigger.title()}**\n\n{PMU_KNOWLEDGE[key]}"
    return None


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    contexte = contexte_analyse or {}
    q = question.lower().strip()
    historique_pmu = contexte.get("historique_pmu") or []

    if any(k in q for k in ["course passée", "course passee", "course d'hier", "hier", "dernier ticket", "ticket d'hier", "arrivée d'hier", "arrivee d'hier"]):
        if historique_pmu:
            h = historique_pmu[-1]
            course = h.get("course") or {}
            arrivee = h.get("arrivee")
            tickets_h = h.get("tickets") or {}
            texte = (
                f"🧠 **Dernière course mémorisée**\n\n"
                f"Course : **{course.get('course', 'Course')}** — {course.get('date', '')} {course.get('reunion', '')}{course.get('course_numero', '')}\n\n"
                f"🎟️ Ticket enregistré : **{tickets_h if tickets_h else 'non disponible'}**"
            )
            if arrivee:
                texte += f"\n🏁 Arrivée officielle enregistrée : **{' - '.join(map(str, arrivee))}**"
            else:
                texte += "\n🏁 Arrivée officielle : **pas encore enregistrée**."
            return {"status": "success", "question": question, "reponse": texte, "intent": "historique"}
        return {"status": "success", "question": question, "reponse": "📚 Je n'ai pas encore de course passée mémorisée dans l'historique serveur.", "intent": "historique"}
    moteur = contexte.get("moteur", {})
    classement = list(moteur.get("classement", []) or [])
    tickets = moteur.get("tickets", {}) or {}
    prenom = str(contexte.get("prenom") or "").strip()

    response = _salutation(q, prenom) or _conversation(q)
    if response:
        return {"status": "success", "question": question, "reponse": response, "intent": "conversation"}

    # Les demandes de ticket/analyse sont prioritaires sur la simple explication du mot "Quinté".
    if not classement:
        if any(k in q for k in ["analyse", "ticket", "course", "quinté", "quinte", "favori", "outsider"]):
            return {"status": "success", "question": question, "reponse": "🏇 Je peux le faire, mais je dois d'abord récupérer les données PMU de la course demandée. Donnez-moi la date, la réunion/course ou dites simplement « analyse la course du jour ». ", "intent": "course"}

    response = _knowledge(q)
    if response and not any(k in q for k in ["ticket", "construis", "fais", "analyse", "base", "favori"]):
        return {"status": "success", "question": question, "reponse": response, "intent": "connaissance_pmu"}

    # Ticket IA indépendant
    if any(k in q for k in ["mon propre", "propre quinté", "ticket ia", "ticket indépendant", "indépendant d'az", "construis", "fais un ticket", "quinté prudent", "quinte prudent", "spéculatif", "value"]):
        style = "prudent" if "prudent" in q else "speculatif" if "spéculatif" in q or "speculatif" in q else "value" if "value" in q else "equilibre"
        ticket = construire_ticket_ia(classement, style)
        nums = [str(x.get("numero")) for x in ticket["selection"]]
        out = [f"N°{x.get('numero')} {x.get('nom')} (cote {x.get('cote_brute', x.get('cote', 'N/D'))})" for x in ticket["outsiders"]]
        reponse = (
            f"🧠 **Mon ticket IA {style}**\n\n"
            f"🎟️ **Quinté : {' - '.join(nums)}**\n\n"
            f"🎯 **Base IA : N°{ticket['base'].get('numero')} {ticket['base'].get('nom')}**\n"
            f"Indice IA : **{ticket['base'].get('score_ia')}/10**\n\n"
            f"🔥 **Outsiders détectés :** {', '.join(out) if out else 'aucun profil > cote 10 disponible'}\n\n"
            "**Pourquoi ?**\n" + "\n".join(f"- {d}" for d in ticket["details"]) +
            "\n\n⚠️ Cette sélection est indépendante du ticket AZ Turf Pro ; elle repose uniquement sur les facteurs disponibles dans les données de course."
        )
        return {"status": "success", "question": question, "reponse": reponse, "intent": "ticket_ia", "ticket_ia": ticket}

    if any(k in q for k in ["favori", "coup sûr", "coup sur", "meilleur cheval", "base"]):
        top = classement[0]
        return {"status": "success", "question": question, "reponse": f"🎯 **Base AZ Turf Pro : N°{top.get('numero')} {top.get('nom')}** — Indice AZ {top.get('indice_az')}, Premium {top.get('indice_premium')}. Si vous voulez ma propre base IA, dites « donne-moi ta base indépendamment d'AZ ». ", "intent": "favori"}

    if any(k in q for k in ["outsider", "tocard", "pépite", "pepite"]):
        ticket = construire_ticket_ia(classement, "value")
        if ticket["outsiders"]:
            x = ticket["outsiders"][0]
            return {"status": "success", "question": question, "reponse": f"🔥 **Outsider IA : N°{x.get('numero')} {x.get('nom')}** — cote {x.get('cote_brute', x.get('cote', 'N/D'))}, score IA {x.get('score_ia')}/10. Je le retiens pour son rapport entre profil et cote, pas simplement parce qu'il est délaissé.", "intent": "outsider"}
        return {"status": "success", "question": question, "reponse": "Je ne vois pas actuellement de cote suffisamment élevée pour qualifier un profil d'outsider avec les données disponibles.", "intent": "outsider"}

    if any(k in q for k in ["scénario", "scenario", "rythme", "course rapide", "course lente"]):
        leaders = classement[:3]
        noms = ", ".join(f"N°{x.get('numero')} {x.get('nom')}" for x in leaders)
        return {"status": "success", "question": question, "reponse": f"🛣️ **Scénario de base**\n\nJe surveillerais en priorité {noms}. Le scénario exact dépend des profils de départ, de la discipline et des données tactiques disponibles. Je peux construire un scénario prudent et un scénario offensif à partir des partants.", "intent": "scenario"}

    if "badge" in q or "signification" in q:
        return {"status": "success", "question": question, "reponse": "🏷️ **Badges AZ Turf Pro**\n- **D4** : déferré des 4 pieds.\n- **Duo Chaud 🔥** : signal lié à l'entourage.\n- **Spécialiste 🎯** : aptitude détectée.\n- **Rachat ⚡** : profil à reconsidérer après une contre-performance.", "intent": "badges"}

    if any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        ticket = construire_ticket_ia(classement, "equilibre")
        nums = [str(x.get("numero")) for x in ticket["selection"]]
        az = (tickets.get("gratuit") or {}).get("quinte", [])
        az_nums = [str(x.get("numero")) for x in az] if az else []
        return {"status": "success", "question": question, "reponse": f"🎟️ **Mon Quinté IA : {' - '.join(nums)}**\n\nTicket AZ disponible : **{' - '.join(az_nums) if az_nums else 'non disponible'}**.\n\nJe peux aussi vous donner une version prudente, spéculative ou Value.", "intent": "quinte", "ticket_ia": ticket}

    return {"status": "success", "question": question, "reponse": "🤖 Je peux vous aider sur pratiquement tout ce qui concerne le PMU : courses passées ou à venir, partants, cotes, favoris, outsiders, tickets, scénarios, règles des paris, analyse IA indépendante et comparaison avec AZ Turf Pro. Dites-moi simplement ce que vous cherchez.", "intent": "general_pmu"}
