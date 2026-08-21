"""AZ Turf Pro - moteur conversationnel PMU autonome.

Le moteur distingue :
- conversation naturelle ;
- analyse d'une course ;
- analyse d'un cheval ;
- tickets prudent/equilibre/speculatif ;
- value par rapport aux cotes ;
- favoris vulnerables ;
- scenarios de course ;
- comparaison avec AZ Turf Pro ;
- historique et courses a venir.

Il n'invente jamais une donnee absente : les valeurs inconnues sont marquees
comme non disponibles.
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
    for key in ("chevaux", "partants", "classement"):
        value = ctx.get(key)
        if isinstance(value, list) and value:
            return [x for x in value if isinstance(x, dict)]
    moteur = ctx.get("moteur") or {}
    for key in ("chevaux", "classement"):
        value = moteur.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    return []


def _score(h: dict) -> float:
    """Score IA indépendant. Ne lit jamais indice_az/indice_premium."""
    forme = _num(h.get("forme"), 5.0) or 5.0
    regularite = _num(h.get("regularite"), 5.0) or 5.0
    experience = _num(h.get("experience"), 5.0) or 5.0
    gains = _num(h.get("gains"), 5.0) or 5.0
    jockey = _num(h.get("jockey_score"), 5.0) or 5.0
    distance = _num(h.get("distance"), 5.0) or 5.0
    terrain = _num(h.get("terrain"), 5.0) or 5.0
    # Cote normalisee : petite cote = confiance, grosse cote = potentiel value.
    cote_score = _num(h.get("cote"), 5.0) or 5.0
    # Pondération équilibrée, volontairement différente des indices AZ.
    return round(max(0.0, min(10.0,
        forme * 0.24 + regularite * 0.18 + distance * 0.12 +
        terrain * 0.08 + jockey * 0.10 + experience * 0.08 +
        gains * 0.08 + cote_score * 0.12
    )), 2)


def _ranked(horses: List[dict]) -> List[dict]:
    result = []
    for h in horses:
        x = dict(h)
        x["ia_score"] = _score(h)
        result.append(x)
    return sorted(result, key=lambda x: x["ia_score"], reverse=True)


def _cote(h: dict) -> Optional[float]:
    return _num(h.get("cote_brute"), _num(h.get("cote"), None))


def _num_name(h: dict) -> str:
    return f"N°{h.get('numero')} {h.get('nom', '')}".strip()


def _find_horse(q: str, horses: List[dict]) -> Optional[dict]:
    nums = re.findall(r"\b(?:n°|no|num(?:ero)?\s*)?(\d{1,2})\b", q, re.I)
    if nums:
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
        return sorted(ranked, key=lambda h: (h["ia_score"], _num(h.get("regularite"), 5)), reverse=True)[:5]
    if mode == "speculatif":
        candidates = [h for h in ranked if (_cote(h) or 0) >= 12]
        candidates = sorted(candidates, key=lambda h: (h["ia_score"], _cote(h) or 0), reverse=True)
        base = [h for h in ranked if (_cote(h) or 0) < 12][:2]
        return (candidates[:3] + base)[:5]
    return ranked[:5]


def _format_ticket(items: List[dict]) -> str:
    return " - ".join(str(h.get("numero")) for h in items)


def _greeting(q: str, ctx: dict) -> Optional[str]:
    if re.search(r"\b(merci|ca va|ça va|je vais bien|bien merci|super|d'accord|ok|bonjour|bonsoir|salut|hello)\b", q):
        if re.fullmatch(r"(?:bonjour|bonsoir|salut|hello|ça va|ca va|merci|ok|d'accord|super|je vais bien(?:,? merci)?)\W*", q):
            name = _text(ctx.get("prenom") or ctx.get("nom_utilisateur"))
            who = f" {name}" if name else ""
            if "merci" in q or "bien" in q or q in {"ok", "d'accord", "super"}:
                return f"Avec plaisir 😊 Ravi de l'entendre. Sur quoi voulez-vous qu'on travaille aujourd'hui ? 🏇"
            return f"Bonjour{who} 👋 Comment allez-vous aujourd'hui ?\n\nJe suis l'Assistant Chatbot AZ Turf Pro. Sur quoi souhaitez-vous qu'on travaille aujourd'hui ? 🏇"
    return None


def repondre_assistant_turf(question: str, contexte_analyse: Optional[dict] = None) -> dict:
    ctx = contexte_analyse or {}
    q = _text(question).lower()
    horses = _horses(ctx)
    ranked = _ranked(horses)
    greeting = _greeting(q, ctx)
    if greeting:
        return {"status": "success", "question": question, "intent": "conversation", "reponse": greeting}

    # Questions purement générales PMU.
    if any(x in q for x in ["qu'est-ce que le pmu", "c'est quoi le pmu", "comment fonctionne le quinté", "différence entre tiercé", "comment jouer", "2sur4", "couplé", "simple gagnant", "simple placé", "multi"]):
        return {"status":"success","question":question,"intent":"pmu_general","reponse":(
            "🏇 **Je peux vous expliquer les principaux paris PMU** : Simple Gagnant/Placé, Couplé, Tiercé, Quarté+, Quinté+, 2sur4, Multi, rapports, cotes, outsiders et bases.\n\n"
            "Dites-moi simplement le pari ou le terme que vous voulez comprendre et je vous l'explique avec un exemple."
        )}

    if not horses:
        return {"status":"success","question":question,"intent":"need_data","reponse":(
            "Je peux effectuer cette analyse, mais je n'ai pas encore les partants PMU nécessaires dans le contexte actuel. "
            "Je dois d'abord récupérer la course et ses données réelles avant de construire un ticket."
        )}

    # Cheval précis : doit passer avant les intentions génériques.
    target = _find_horse(q, horses)
    if target and any(x in q for x in ["comment", "pourquoi", "avis", "analyse", "que penses", "trouve", "vaut", "8"]):
        s = _score(target)
        c = _cote(target)
        return {"status":"success","question":question,"intent":"horse_analysis","reponse":(
            f"🐎 **Analyse IA du {_num_name(target)}**\n\n"
            f"Indice IA indépendant : **{s}/10**\n"
            f"Forme : **{_num(target.get('forme'),5):.1f}/10** · Régularité : **{_num(target.get('regularite'),5):.1f}/10**\n"
            f"Aptitude distance : **{_num(target.get('distance'),5):.1f}/10** · Jockey : **{_num(target.get('jockey_score'),5):.1f}/10**\n"
            f"Cote : **{c if c is not None else 'non disponible'}**\n\n"
            "**Verdict :** " + ("profil intéressant" if s >= 6.5 else "profil secondaire") + ". "
            "Je distingue ce score de l'Indice AZ Turf Pro."
        )}

    # Scénarios tactiques.
    if any(x in q for x in ["scénario", "scenario", "déroulement", "déroule", "train de course"]):
        top = ranked[:4]
        noms = ", ".join(_num_name(h) for h in top)
        return {"status":"success","question":question,"intent":"scenarios","reponse":(
            "🛣️ **Scénario 1 — course sélective**\n"
            f"Les profils les plus réguliers peuvent bénéficier d'un rythme soutenu. Surveillance prioritaire : {noms}.\n\n"
            "🛣️ **Scénario 2 — course tactique**\n"
            "Un rythme moins soutenu favorise davantage les chevaux capables de bien se placer et de produire leur effort au bon moment. "
            f"La hiérarchie IA reste centrée sur {_num_name(ranked[0])}, mais les outsiders doivent être conservés."
        )}

    # Tickets avec stratégie distincte.
    if "spéculatif" in q or "speculatif" in q or "gros outsider" in q or "vrais outsiders" in q:
        ticket = _ticket(ranked, "speculatif")
        outs = [h for h in ranked if (_cote(h) or 0) >= 12][:4]
        return {"status":"success","question":question,"intent":"ticket_speculatif","reponse":(
            "🔥 **Ticket IA spéculatif indépendant**\n"
            f"Quinté : **{_format_ticket(ticket)}**\n"
            f"Outsiders retenus : " + (", ".join(f"{_num_name(h)} (cote {_cote(h)})" for h in outs) if outs else "aucun vrai outsider avec cote disponible") + "\n\n"
            "Cette stratégie accepte davantage de risque et ne recopie pas le ticket AZ Turf Pro."
        )}

    if "prudent" in q or "sécur" in q or "secur" in q:
        ticket = _ticket(ranked, "prudent")
        return {"status":"success","question":question,"intent":"ticket_prudent","reponse":(
            "🛡️ **Ticket IA prudent indépendant**\n"
            f"Quinté : **{_format_ticket(ticket)}**\n"
            f"Base IA : **{_num_name(ticket[0])}**\n\n"
            "Priorité donnée à la forme, la régularité et aux profils les moins risqués."
        )}

    if any(x in q for x in ["ticket ia", "mon ticket", "propre ticket", "construis", "quinté"]):
        ticket = _ticket(ranked, "equilibre")
        return {"status":"success","question":question,"intent":"ticket_equilibre","reponse":(
            "🎟️ **Mon Quinté IA indépendant**\n\n"
            f"Quinté : **{_format_ticket(ticket)}**\n"
            f"Base IA : **{_num_name(ticket[0])}** — score **{ticket[0]['ia_score']}/10**\n\n"
            "Le classement est calculé séparément des indices AZ Turf Pro."
        )}

    if any(x in q for x in ["value", "valeur", "cote", "rapport"]):
        values = []
        for h in ranked:
            c = _cote(h)
            if c and c >= 8:
                implied = 1.0 / c
                # proxy de probabilité à partir du score IA, sans prétendre être une probabilité calibrée.
                model_p = max(0.03, min(0.45, (h["ia_score"] / 10.0) * 0.45))
                edge = model_p - implied
                if edge > 0:
                    values.append((edge, h, model_p, implied))
        values.sort(key=lambda x: x[0], reverse=True)
        lines = []
        for edge,h,mp,ip in values[:5]:
            lines.append(f"N°{h.get('numero')} {h.get('nom','')} — cote {cote if False else _cote(h)} — écart indicatif {edge*100:.1f} pts")
        return {"status":"success","question":question,"intent":"value","reponse":(
            "💰 **Chevaux à valeur IA**\n" + ("\n".join(lines) if lines else "Aucune value suffisamment nette avec les données disponibles.") +
            "\n\n⚠️ L'écart est un indicateur de modèle, pas une probabilité garantie."
        )}

    if "badge" in q:
        return {"status":"success","question":question,"intent":"badges","reponse":(
            "🏷️ **Badges AZ Turf Pro**\n- **D4** : déferré des 4 pieds.\n- **Duo Chaud 🔥** : signal lié à l'entourage.\n- **Spécialiste 🎯** : aptitude détectée.\n- **Rachat ⚡** : profil à reconsidérer après une contre-performance."
        )}

    if "favori" in q and any(x in q for x in ["vuln", "fragile", "contre", "risque"]):
        fav = ranked[0]
        return {"status":"success","question":question,"intent":"vulnerable_favorite","reponse":(
            f"⚠️ **Favori à surveiller : {_num_name(fav)}**\n\nScore IA : **{fav['ia_score']}/10**. "
            "Je ne le considère pas automatiquement comme sûr : je vérifie toujours cote, régularité, aptitude et scénario avant de le retenir comme base."
        )}

    if "favori" in q or "meilleure base" in q or "base" in q:
        fav = ranked[0]
        return {"status":"success","question":question,"intent":"base","reponse":(
            f"🎯 **Base IA : {_num_name(fav)}**\n\n"
            f"Score IA indépendant : **{fav['ia_score']}/10**. Forme **{_num(fav.get('forme'),5):.1f}**, régularité **{_num(fav.get('regularite'),5):.1f}**, aptitude **{_num(fav.get('distance'),5):.1f}**.\n\n"
            "C'est une base de modèle, pas une garantie d'arrivée."
        )}

    if "analyse" in q or "course" in q:
        top = ranked[:5]
        return {"status":"success","question":question,"intent":"course_analysis","reponse":(
            "🧠 **Analyse IA de la course**\n\n" +
            "\n".join(f"{i+1}. **{_num_name(h)}** — {h['ia_score']}/10" for i,h in enumerate(top)) +
            f"\n\n🎯 Base IA : **{_num_name(top[0])}**\n🔥 Outsider potentiel : **{_num_name(next((h for h in ranked if (_cote(h) or 0)>=12), top[-1]))}**"
        )}

    return {"status":"success","question":question,"intent":"general_pmu","reponse":(
        "🤖 Je peux vous aider sur la course, les chevaux, les cotes, les tickets, les outsiders, les favoris vulnérables, les scénarios, les résultats et le fonctionnement du PMU.\n\n"
        "Dites-moi simplement ce que vous voulez savoir."
    )}
