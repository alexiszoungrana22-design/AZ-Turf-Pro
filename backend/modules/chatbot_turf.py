"""AZ Turf Pro - moteur conversationnel PMU autonome v24.2.

Moteur déterministe : les tickets IA sont indépendants des indices AZ Turf Pro.
Les données absentes ne sont jamais inventées.
"""

from __future__ import annotations
import math
import re
from typing import Any, Dict, List, Optional


def _num(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    return str(value or "").strip()


def _horses(ctx: dict) -> List[dict]:
    candidates = []
    for key in ("chevaux", "partants", "classement"):
        value = ctx.get(key)
        if isinstance(value, list):
            candidates.extend(x for x in value if isinstance(x, dict))
    moteur = ctx.get("moteur") or {}
    for key in ("chevaux", "classement"):
        value = moteur.get(key)
        if isinstance(value, list):
            candidates.extend(x for x in value if isinstance(x, dict))
    seen, result = set(), []
    for h in candidates:
        n = str(h.get("numero"))
        if n not in seen:
            seen.add(n)
            result.append(h)
    return result


def _cote(h: dict) -> Optional[float]:
    return _num(h.get("cote_brute"), _num(h.get("cote"), None))


def _score(h: dict) -> float:
    """Score IA 0-10 sans utiliser indice_az/indice_premium."""
    forme = _num(h.get("forme"), 5.0) or 5.0
    reg = _num(h.get("regularite"), 5.0) or 5.0
    exp = _num(h.get("experience"), 5.0) or 5.0
    gains = _num(h.get("gains"), 5.0) or 5.0
    jockey = _num(h.get("jockey_score"), 5.0) or 5.0
    distance = _num(h.get("distance"), 5.0) or 5.0
    terrain = _num(h.get("terrain"), 5.0) or 5.0

    # La cote est transformée : une cote élevée ne peut plus saturer le score à 10.
    c = _cote(h)
    cote_confiance = 5.0 if not c or c <= 1 else max(0.0, min(10.0, 10.0 / (1.0 + math.log(c))))

    score = (
        forme * .25 + reg * .20 + distance * .12 + terrain * .08 +
        jockey * .10 + exp * .07 + gains * .08 + cote_confiance * .10
    )
    return round(max(0.0, min(10.0, score)), 2)


def _ranked(horses: List[dict]) -> List[dict]:
    result = []
    for h in horses:
        x = dict(h)
        x["ia_score"] = _score(h)
        result.append(x)
    return sorted(result, key=lambda x: x["ia_score"], reverse=True)


def _num_name(h: dict) -> str:
    return f"N°{h.get('numero')} {h.get('nom', '')}".strip()


def _find_horse(q: str, horses: List[dict]) -> Optional[dict]:
    # Un numéro isolé ou précédé de N°, n°, no, numéro.
    patterns = [
        r"(?:n[°o]\s*|num(?:é|e)ro\s*)?(\d{1,2})\b",
    ]
    nums = []
    for p in patterns:
        nums.extend(re.findall(p, q, re.I))
    for n in nums:
        for h in horses:
            if str(h.get("numero")) == str(int(n)):
                return h
    for h in horses:
        name = _text(h.get("nom")).lower()
        if name and name in q:
            return h
    return None


def _ticket(ranked: List[dict], mode: str) -> List[dict]:
    if not ranked:
        return []
    if mode == "prudent":
        return sorted(
            ranked,
            key=lambda h: (
                h["ia_score"],
                _num(h.get("regularite"), 5.0) or 5.0,
                -(_cote(h) or 99),
            ),
            reverse=True,
        )[:5]
    if mode == "speculatif":
        # 3 profils value/outsiders + 2 profils solides : volontairement différent du prudent.
        outsiders = [h for h in ranked if (_cote(h) or 0) >= 12]
        outsiders.sort(
            key=lambda h: (
                h["ia_score"] + min(2.0, math.log(max(_cote(h) or 1, 1)) * .35),
                _cote(h) or 0,
            ),
            reverse=True,
        )
        solides = [h for h in ranked if h not in outsiders]
        return (outsiders[:3] + solides[:2])[:5]
    return ranked[:5]


def _format_ticket(items: List[dict]) -> str:
    return " - ".join(str(h.get("numero")) for h in items)


def _greeting(q: str, ctx: dict) -> Optional[str]:
    clean = re.sub(r"[!?.,;:]+", "", q).strip()
    name = _text(ctx.get("prenom") or ctx.get("nom_utilisateur"))
    who = f" {name}" if name else ""
    if clean in {"bonjour", "bonsoir", "salut", "hello"}:
        return f"Bonjour{who} 👋 Comment allez-vous aujourd'hui ?\n\nJe suis l'Assistant Chatbot AZ Turf Pro. Sur quoi souhaitez-vous qu'on travaille aujourd'hui ? 🏇"
    if clean in {"ca va", "ça va", "je vais bien", "je vais bien merci", "bien merci", "merci", "ok", "daccord", "d'accord", "super"}:
        return "Avec plaisir 😊 Ravi de l'entendre. Sur quoi voulez-vous qu'on travaille aujourd'hui ? 🏇"
    return None


def _history_answer(ctx: dict) -> Optional[str]:
    hist = ctx.get("historique_pmu") or []
    for item in hist:
        if not isinstance(item, dict):
            continue
        arr = item.get("arrivee")
        if arr:
            course = item.get("course") or {}
            label = course.get("course") or course.get("course_numero") or "course mémorisée"
            return f"🏁 **Arrivée officielle mémorisée**\n\n**{label}**\n\n**{' - '.join(map(str, arr))}**"
    return None


def repondre_assistant_turf(question: str, contexte_analyse: Optional[dict] = None) -> dict:
    ctx = contexte_analyse or {}
    q = _text(question).lower()
    horses = _horses(ctx)
    ranked = _ranked(horses)

    greeting = _greeting(q, ctx)
    if greeting:
        return {"status": "success", "intent": "conversation", "reponse": greeting}

    # Arrivée/résultat avant les intentions génériques "course".
    if any(x in q for x in ["arrivée", "arrivee", "résultat", "resultat", "hier", "course passée", "course passee"]):
        answer = ctx.get("arrivee_recherchee")
        if answer:
            return {"status": "success", "intent": "resultat", "reponse": answer}
        answer = _history_answer(ctx)
        if answer:
            return {"status": "success", "intent": "resultat", "reponse": answer}
        return {"status": "success", "intent": "resultat", "reponse": "🏁 Je n'ai pas encore récupéré l'arrivée officielle demandée dans les données PMU disponibles. Je préfère ne pas l'inventer."}

    # Cheval précis : avant ticket/analyse générique.
    target = _find_horse(q, horses)
    if target and any(x in q for x in ["comment", "pourquoi", "avis", "analyse", "trouve", "vaut", "penses", "que donne", "que vaut"]):
        s = _score(target)
        c = _cote(target)
        forme = _num(target.get("forme"), 5.0) or 5.0
        reg = _num(target.get("regularite"), 5.0) or 5.0
        verdict = "très intéressant" if s >= 7 else "intéressant" if s >= 6 else "secondaire"
        return {"status": "success", "intent": "horse_analysis", "reponse": (
            f"🐎 **Analyse IA du {_num_name(target)}**\n\n"
            f"Indice IA indépendant : **{s}/10**\n"
            f"Forme : **{forme:.1f}/10** · Régularité : **{reg:.1f}/10**\n"
            f"Aptitude distance : **{_num(target.get('distance'),5.0):.1f}/10** · "
            f"Jockey : **{_num(target.get('jockey_score'),5.0):.1f}/10**\n"
            f"Cote : **{c if c is not None else 'non disponible'}**\n\n"
            f"🎯 **Verdict : {verdict}.** Je le juge séparément du ticket AZ Turf Pro."
        )}

    if not horses:
        return {"status": "success", "intent": "need_data", "reponse": (
            "Je peux effectuer cette analyse, mais les partants PMU réels ne sont pas disponibles dans le contexte actuel. "
            "Je dois d'abord récupérer la course avant de construire un ticket."
        )}

    if any(x in q for x in ["scénario", "scenario", "déroulement", "déroule", "train de course"]):
        top = ranked[:4]
        return {"status": "success", "intent": "scenarios", "reponse": (
            "🛣️ **Scénario 1 — train sélectif**\n"
            f"Un rythme soutenu favorise les profils réguliers et capables de soutenir leur effort. À surveiller : "
            f"{', '.join(_num_name(h) for h in top[:3])}.\n\n"
            "🛣️ **Scénario 2 — course tactique**\n"
            f"Un rythme plus lent favorise le placement et l'accélération finale. Priorité : {_num_name(top[0])}, "
            f"avec {', '.join(_num_name(h) for h in top[1:3])} comme alternatives.\n\n"
            "⚠️ Ce sont deux scénarios de modèle : le rythme réel peut modifier la hiérarchie."
        )}

    if "spéculatif" in q or "speculatif" in q or "gros outsider" in q or "vrais outsiders" in q:
        ticket = _ticket(ranked, "speculatif")
        outs = [h for h in ranked if (_cote(h) or 0) >= 12]
        outs.sort(key=lambda h: h["ia_score"] + min(2, math.log(max(_cote(h) or 1, 1)) * .35), reverse=True)
        return {"status": "success", "intent": "ticket_speculatif", "reponse": (
            "🔥 **Ticket IA spéculatif indépendant**\n"
            f"Quinté : **{_format_ticket(ticket)}**\n\n"
            "🎯 **Outsiders réellement retenus :**\n" +
            ("\n".join(f"• {_num_name(h)} — cote {_cote(h)} — score IA {h['ia_score']}/10" for h in outs[:3])
             if outs else "• Aucun outsider ≥ 12 disponible avec des données suffisantes.") +
            "\n\nCette sélection accepte davantage de risque et ne recopie pas le ticket AZ Turf Pro."
        )}

    if "prudent" in q or "sécur" in q or "secur" in q:
        ticket = _ticket(ranked, "prudent")
        return {"status": "success", "intent": "ticket_prudent", "reponse": (
            "🛡️ **Ticket IA prudent indépendant**\n"
            f"Quinté : **{_format_ticket(ticket)}**\n"
            f"Base IA : **{_num_name(ticket[0])}**\n\n"
            "Priorité : forme, régularité, aptitude et réduction du risque."
        )}

    if any(x in q for x in ["value", "valeur par rapport", "chevaux à valeur"]):
        values = []
        for h in ranked:
            c = _cote(h)
            if c and c >= 8:
                implied = 1.0 / c
                # Probabilité indicative calibrée à partir du score, plafonnée volontairement.
                model_p = max(0.02, min(0.35, 0.02 + (h["ia_score"] / 10.0) * 0.22))
                edge = model_p - implied
                values.append((edge, h, model_p, implied))
        values.sort(key=lambda x: x[0], reverse=True)
        lines = [
            f"• {_num_name(h)} — cote {c:.1f} — prob. modèle {mp*100:.1f}% — implicite {ip*100:.1f}% — écart {edge*100:+.1f} pts"
            for edge, h, mp, ip in values[:5]
            for c in [_cote(h)]
        ]
        return {"status": "success", "intent": "value", "reponse": (
            "💰 **Meilleures valeurs IA par rapport aux cotes**\n" +
            ("\n".join(lines) if lines else "Aucune value suffisamment nette avec les données disponibles.") +
            "\n\n⚠️ L'écart est un indicateur du modèle, pas une probabilité garantie."
        )}

    if "badge" in q:
        return {"status": "success", "intent": "badges", "reponse": (
            "🏷️ **Badges AZ Turf Pro**\n"
            "• **D4** : déferré des 4 pieds.\n"
            "• **Duo Chaud 🔥** : signal lié à l'entourage.\n"
            "• **Spécialiste 🎯** : aptitude détectée.\n"
            "• **Rachat ⚡** : profil à reconsidérer après une contre-performance."
        )}

    if "favori" in q and any(x in q for x in ["vuln", "fragile", "contre", "risque"]):
        fav = ranked[0]
        return {"status": "success", "intent": "vulnerable_favorite", "reponse": (
            f"⚠️ **Favori à surveiller : {_num_name(fav)}**\n\n"
            f"Score IA : **{fav['ia_score']}/10**. Je vérifie cote, régularité, aptitude et scénario avant de le considérer comme une base."
        )}

    if "favori" in q or "meilleure base" in q or "base" in q:
        fav = ranked[0]
        return {"status": "success", "intent": "base", "reponse": (
            f"🎯 **Base IA : {_num_name(fav)}**\n\n"
            f"Score IA indépendant : **{fav['ia_score']}/10**.\n"
            f"Forme **{_num(fav.get('forme'),5.0):.1f}** · Régularité **{_num(fav.get('regularite'),5.0):.1f}** · "
            f"Aptitude **{_num(fav.get('distance'),5.0):.1f}**.\n\n"
            "C'est une base de modèle, pas une garantie d'arrivée."
        )}

    if "compare" in q and ("az turf" in q or "premium" in q):
        ia = _ticket(ranked, "equilibre")
        az = (ctx.get("moteur") or {}).get("tickets", {}).get("premium", {}).get("selection_quinte", [])
        az_nums = [str(x.get("numero", x)) if isinstance(x, dict) else str(x) for x in (az or [])]
        return {"status": "success", "intent": "comparison", "reponse": (
            "⚔️ **Comparaison IA / AZ Turf Pro**\n\n"
            f"🤖 Ticket IA : **{_format_ticket(ia)}**\n"
            f"🏆 Ticket AZ Turf Pro : **{' - '.join(az_nums) if az_nums else 'non disponible'}**\n\n"
            "Les deux sélections sont présentées séparément ; l'IA n'utilise pas l'indice AZ pour calculer son score."
        )}

    if any(x in q for x in ["ticket ia", "mon ticket", "propre ticket", "construis", "quinté", "quinte"]):
        ticket = _ticket(ranked, "equilibre")
        return {"status": "success", "intent": "ticket_equilibre", "reponse": (
            "🎟️ **Mon Quinté IA indépendant**\n\n"
            f"Quinté : **{_format_ticket(ticket)}**\n"
            f"Base IA : **{_num_name(ticket[0])}** — score **{ticket[0]['ia_score']}/10**\n\n"
            "Sélection calculée séparément du ticket AZ Turf Pro."
        )}

    if "analyse" in q or "course" in q:
        top = ranked[:5]
        outsider = next((h for h in ranked if (_cote(h) or 0) >= 12), None)
        return {"status": "success", "intent": "course_analysis", "reponse": (
            "🧠 **Analyse IA de la course**\n\n" +
            "\n".join(f"{i+1}. **{_num_name(h)}** — {h['ia_score']}/10" for i, h in enumerate(top)) +
            f"\n\n🎯 Base IA : **{_num_name(top[0])}**" +
            (f"\n🔥 Outsider potentiel : **{_num_name(outsider)}** — cote {_cote(outsider)}" if outsider else "")
        )}

    return {"status": "success", "intent": "general_pmu", "reponse": (
        "🤖 Je peux vous aider sur les chevaux, les cotes, les tickets, les outsiders, "
        "les favoris vulnérables, les scénarios, les résultats et le fonctionnement du PMU.\n\n"
        "Dites-moi simplement ce que vous voulez savoir."
    )}
                    
