"""
AZ TURF PRO - Assistant conversationnel IA
v23.4 - moteur de tickets IA independant du moteur AZ Turf Pro.

Le moteur IA utilise uniquement les donnees de la course fournies par PMU
(cote, forme, regularite, gains, experience, jockey) pour construire ses
propres scores et combinaisons. Les tickets AZ ne servent qu'a la comparaison.
"""

import math
import re


def _num(v, default=0.0):
    try:
        if v is None or v == "":
            return float(default)
        return float(v)
    except (TypeError, ValueError):
        return float(default)


def _clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, float(v)))


def _positions(perfs):
    if isinstance(perfs, list):
        out = []
        for p in perfs:
            try:
                n = int(p)
                if 1 <= n <= 30:
                    out.append(n)
            except (TypeError, ValueError):
                pass
        return out
    text = str(perfs or "")
    nums = []
    for token in re.findall(r"\d+", text):
        n = int(token)
        if 1 <= n <= 30:
            nums.append(n)
    return nums


def _score_form(c):
    if c.get("forme") is not None:
        return _clamp(_num(c.get("forme"), 5))
    pos = _positions(c.get("performances") or c.get("musique_brute"))
    if not pos:
        return 5.0
    weights = [1.0, 0.9, 0.8, 0.7, 0.6]
    vals = []
    for i, p in enumerate(pos[:5]):
        vals.append(max(0.0, 11.0 - p) * weights[i])
    return _clamp(sum(vals) / max(sum(weights[:len(vals)]), 1.0))


def _score_regularite(c):
    if c.get("regularite") is not None:
        return _clamp(_num(c.get("regularite"), 5))
    pos = _positions(c.get("performances") or c.get("musique_brute"))
    if not pos:
        return 5.0
    return _clamp(10.0 - (sum(abs(p - 5) for p in pos[:6]) / max(len(pos[:6]), 1)))


def _score_cote(c, all_cotes):
    cote = _num(c.get("cote_brute"), 0)
    if cote <= 0:
        return 5.0, cote
    valid = sorted(x for x in all_cotes if x > 0)
    if not valid:
        return 5.0, cote
    # Score marche: les cotes basses sont favorables, mais on ne laisse
    # jamais la cote dominer l'algorithme.
    lo, hi = valid[0], valid[-1]
    if hi == lo:
        return 5.0, cote
    market = 10.0 - ((cote - lo) / (hi - lo)) * 10.0
    return _clamp(market), cote


def _score_value(score, cote):
    if cote <= 0:
        return 5.0
    # Probabilite implicite du modele (softmax simplifiee) x cote.
    # On cherche la valeur, pas seulement le favori de marche.
    implied = 1.0 / cote
    model_prob = max(0.02, min(0.45, score / 22.0))
    raw = (model_prob / implied) * 5.0
    return _clamp(raw)


def _analyse_chevaux(chevaux):
    actifs = [c for c in chevaux if isinstance(c, dict) and c.get("numero") is not None]
    cotes = [_num(c.get("cote_brute"), 0) for c in actifs]
    resultats = []

    for c in actifs:
        forme = _score_form(c)
        regularite = _score_regularite(c)
        gains = _clamp(_num(c.get("gains"), 5))
        experience = _clamp(_num(c.get("experience"), 5))
        jockey = _clamp(_num(c.get("jockey_score"), 5))
        cote_score, cote = _score_cote(c, cotes)

        # Score IA independant: aucun indice_az / indice_premium / ticket AZ.
        base = (
            forme * 0.30
            + regularite * 0.20
            + cote_score * 0.15
            + gains * 0.12
            + experience * 0.10
            + jockey * 0.08
        )
        value = _score_value(base, cote)
        score = _clamp(base * 0.85 + value * 0.15)

        resultats.append({
            "numero": c.get("numero"),
            "nom": c.get("nom", ""),
            "cote": cote,
            "score_ia": round(score, 2),
            "forme": round(forme, 2),
            "regularite": round(regularite, 2),
            "valeur": round(value, 2),
            "gains": round(gains, 2),
            "experience": round(experience, 2),
            "jockey": round(jockey, 2),
            "performances": c.get("performances") or c.get("musique_brute") or "",
        })

    resultats.sort(key=lambda x: (x["score_ia"], x["valeur"], x["forme"]), reverse=True)
    return resultats


def construire_ticket_ia(contexte):
    chevaux = (contexte or {}).get("chevaux", [])
    scores = _analyse_chevaux(chevaux)
    if len(scores) < 5:
        return {"scores": scores, "erreur": "Pas assez de partants exploitables pour construire un Quinté."}

    prudent = scores[:5]
    # Sixieme cheval de couverture choisi par score, en évitant les doublons.
    couverture = scores[5:8]
    ticket_prudent = prudent[:5]

    # Ticket spéculatif: conserve 3 profils solides et ajoute les meilleurs
    # outsiders >= 10.0, puis complète avec le meilleur score restant.
    outsiders = [x for x in scores if x["cote"] >= 10.0]
    spec = prudent[:3]
    for outsider in outsiders[:2]:
        if outsider not in spec:
            spec.append(outsider)
    for x in scores:
        if len(spec) >= 5:
            break
        if x not in spec:
            spec.append(x)

    # Sélection IA élargie de 8 chevaux.
    selection = scores[:8]
    return {
        "scores": scores,
        "base": scores[0],
        "ticket_prudent": ticket_prudent,
        "ticket_speculatif": spec[:5],
        "selection_8": selection,
        "couverture": couverture[:3],
        "outsiders": outsiders[:5],
    }


def _nums(items):
    return " - ".join(str(x.get("numero")) for x in items if x.get("numero") is not None)


def _ticket_complet(ticket):
    return (
        f"🎟️ **Ticket IA indépendant**\n"
        f"• Quinté prudent : **{_nums(ticket['ticket_prudent'])}**\n"
        f"• Quinté spéculatif : **{_nums(ticket['ticket_speculatif'])}**\n"
        f"• Sélection élargie : **{_nums(ticket['selection_8'])}**\n"
        f"• Base IA : **N°{ticket['base']['numero']} {ticket['base']['nom']}**"
    )


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = question.lower().strip()
    contexte = contexte_analyse or {}
    moteur = contexte.get("moteur", {})
    classement_az = moteur.get("classement", [])
    tickets_az = moteur.get("tickets", {})
    ticket = construire_ticket_ia(contexte)

    if ticket.get("erreur"):
        return {"status": "error", "question": question, "reponse": ticket["erreur"]}

    # Tickets IA independants: cette branche est prioritaire sur les tickets AZ.
    if any(k in q for k in ["construis ton propre", "indépendamment", "independamment", "ticket ia", "ticket ai", "fais un ticket", "propre quinté"]):
        reponse = _ticket_complet(ticket) + (
            "\n\n🧠 Ce ticket est calculé indépendamment du ticket AZ Turf Pro "
            "à partir de la forme, régularité, cote, valeur, gains, expérience et jockey."
        )
    elif "prudent" in q:
        reponse = f"🛡️ **Ticket IA prudent : {_nums(ticket['ticket_prudent'])}**\nBase : N°{ticket['base']['numero']} {ticket['base']['nom']}"
    elif any(k in q for k in ["spéculatif", "speculatif", "outsider"]):
        reponse = f"🔥 **Ticket IA spéculatif : {_nums(ticket['ticket_speculatif'])}**\nOutsiders retenus : {_nums(ticket['outsiders'][:2]) or 'aucun'}"
    elif any(k in q for k in ["valeur", "value"]):
        top = sorted(ticket["scores"], key=lambda x: x["valeur"], reverse=True)[:3]
        reponse = "💰 **Meilleures valeurs IA :**\n" + "\n".join(
            f"- N°{x['numero']} {x['nom']} — cote {x['cote'] or '?'} — valeur IA {x['valeur']}"
            for x in top
        )
    elif any(k in q for k in ["compare", "az turf pro"]):
        az = tickets_az.get("gratuit", {}) if isinstance(tickets_az, dict) else {}
        azq = az.get("quinte", []) if isinstance(az, dict) else []
        az_nums = _nums(azq) if isinstance(azq, list) else ""
        reponse = (
            f"⚔️ **Comparaison**\n\n"
            f"• Ticket IA indépendant : **{_nums(ticket['ticket_prudent'])}**\n"
            f"• Ticket AZ Turf Pro : **{az_nums or 'non disponible'}**\n\n"
            f"L'IA calcule son propre classement avant de comparer les deux sélections."
        )
    elif any(k in q for k in ["favori", "coup sur", "meilleure base", "base"]):
        b = ticket["base"]
        reponse = f"🎯 **Base IA : N°{b['numero']} {b['nom']}** — score IA **{b['score_ia']}/10**. Forme {b['forme']}, régularité {b['regularite']}, valeur {b['valeur']}."
    elif any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        reponse = _ticket_complet(ticket)
    elif any(k in q for k in ["outsider", "tocard", "surprise", "pépite", "pepite"]):
        outs = ticket["outsiders"]
        if outs:
            x = outs[0]
            reponse = f"🔥 **Outsider IA : N°{x['numero']} {x['nom']}** — cote {x['cote']} — score IA {x['score_ia']}/10, valeur {x['valeur']}/10."
        else:
            reponse = "Aucun outsider avec cote >= 10 n'a obtenu un score IA suffisant."
    elif "badge" in q or "signification" in q:
        reponse = (
            "🏷️ **Guide des badges AZ Turf Pro**\n"
            "- **D4** : Déferré des 4 pieds.\n"
            "- **Duo Chaud 🔥** : signal lié à l'entourage.\n"
            "- **Spécialiste 🎯** : aptitude détectée.\n"
            "- **Rachat ⚡** : profil à reconsidérer après une contre-performance."
        )
    else:
        top = ticket["base"]
        reponse = (
            f"Je peux construire mon propre ticket à partir des partants PMU. "
            f"Pour commencer : **{_nums(ticket['ticket_prudent'])}**. "
            f"Ma base IA est le N°{top['numero']} {top['nom']}."
        )

    return {"status": "success", "question": question, "reponse": reponse, "ia_ticket": ticket}
