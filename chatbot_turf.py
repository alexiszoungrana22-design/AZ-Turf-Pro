"""AZ TURF PRO - Assistant conversationnel, routes inchangées."""
from typing import Any

def _f(v, d=0.0):
    try: return float(str(v).replace(",", "."))
    except (TypeError, ValueError): return d

def _num(c): return str(c.get("numero") or c.get("num") or "?")
def _nom(c): return str(c.get("nom") or "Cheval sans nom")
def _indice(c): return _f(c.get("indice_az", c.get("indice", 0)))
def _premium(c): return _f(c.get("indice_premium", 0))
def _cote(c): return _f(c.get("cote", c.get("cote_brute", 0)))

def _tri(chevaux):
    return sorted([c for c in chevaux if isinstance(c, dict)],
                  key=lambda c: (_indice(c), _premium(c)), reverse=True)

def _ticket(chevaux, speculative=False):
    if speculative:
        outs = [c for c in chevaux if _cote(c) >= 10]
        return sorted(outs or chevaux, key=lambda c: (_premium(c), _indice(c)), reverse=True)[:5]
    return _tri(chevaux)[:5]

def _txt_ticket(xs):
    return " - ".join(_num(c) for c in xs) if xs else "Données indisponibles"

def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = str(question or "").strip().lower()
    ctx = contexte_analyse or {}
    moteur = ctx.get("moteur") or {}
    chevaux = moteur.get("classement") or ctx.get("partants") or []
    tickets = moteur.get("tickets") or {}
    az = ((tickets.get("gratuit") or {}).get("quinte") or [])
    cotes = ctx.get("cotes") or {}
    presse = ctx.get("presse") or {}
    meteo = ctx.get("meteo") or {}
    historique = ctx.get("historique") or []

    # Mémoire conversationnelle : exploite le dernier échange reçu par la route.
    precedent = historique[-1].get("content", "") if historique and isinstance(historique[-1], dict) else ""

    if q in {"bonjour", "bonsoir", "salut", "hello", "coucou", "bjr"}:
        rep = ("👋 **Assistant AZ Turf Pro en ligne.**\n\n"
               "Je peux analyser la course, construire un Quinté IA, "
               "étudier les cotes/Smart Money, comparer les tickets, "
               "analyser la météo/piste, les favoris, les scénarios, "
               "les statistiques et le backtest.")

    elif "analyse la course" in q or q == "analyse" or "course du jour" in q or "analyser" in q:
        top = _tri(chevaux)
        top3 = ", ".join(f"N°{_num(c)} {_nom(c)}" for c in top[:3]) or "indisponible"
        rep = (f"🧠 **Analyse AZ Turf Pro**\n\n"
               f"🎯 Top 3 : {top3}\n"
               f"🌦️ Impact piste/météo : {meteo.get('impact', 'NEUTRE')}\n"
               f"📈 Signaux de cotes : {len(cotes.get('resultats', []))} chevaux analysés.")

    elif "propre quinté" in q or ("quinté" in q and "indépend" in q):
        rep = f"🤖 **Quinté IA indépendant** : **{_txt_ticket(_ticket(chevaux))}**"

    elif "ticket" in q and ("prudent" in q or "sécur" in q):
        rep = f"🛡️ **Ticket IA prudent** : **{_txt_ticket(_ticket(chevaux))}**"

    elif "ticket" in q and ("spéculatif" in q or "speculatif" in q or "outsider" in q):
        rep = f"🔥 **Ticket IA spéculatif** : **{_txt_ticket(_ticket(chevaux, True))}**"

    elif "valeur" in q or "cotes" in q or "cote" in q or "smart money" in q:
        rs = cotes.get("resultats", [])
        smart = [r for r in rs if "SMART_MONEY" in str(r.get("signal", ""))]
        if smart:
            rep = "💰 **Smart Money détecté** :\n" + "\n".join(
                f"- N°{r.get('numero')} {r.get('nom','')} : {r.get('variation_pct')}%"
                for r in smart
            )
        else:
            rep = "💰 Aucun signal Smart Money confirmé dans les variations de cotes disponibles."

    elif "compare" in q and ("ticket" in q or "az turf" in q):
        ia = {_num(c) for c in _ticket(chevaux)}
        azs = {_num(c) for c in az}
        rep = (f"⚔️ **Comparaison IA / AZ Turf Pro**\n"
               f"- IA : **{_txt_ticket(_ticket(chevaux))}**\n"
               f"- AZ : **{_txt_ticket(az)}**\n"
               f"- Communs : **{', '.join(sorted(ia & azs)) or 'aucun'}**")

    elif "meilleure base" in q or ("base" in q and "pourquoi" in q):
        top = _tri(chevaux)
        if top:
            c = top[0]
            rep = f"🎯 **Meilleure base : N°{_num(c)} {_nom(c)}** — Indice AZ {_indice(c):g}, Premium {_premium(c):g}."
        else:
            rep = "Impossible de déterminer une base sans classement."

    elif "favori" in q and ("vulnér" in q or "fragile" in q or "piège" in q):
        top = _tri(chevaux)
        if len(top) >= 2:
            rep = (f"⚠️ **Favori à surveiller** : N°{_num(top[0])} {_nom(top[0])}.\n"
                   f"Concurrent immédiat : N°{_num(top[1])} {_nom(top[1])}.")
        else:
            rep = "Classement insuffisant pour analyser les favoris."

    elif "scénario" in q or "scenario" in q or "déroulement" in q or "tactique" in q:
        top = _tri(chevaux)
        if top:
            out = [c for c in top if _cote(c) >= 10]
            surprise = out[0] if out else top[-1]
            rep = (f"🛣️ **Scénario 1 — Linéaire** : N°{_num(top[0])} {_nom(top[0])} comme point d'appui.\n\n"
                   f"🛣️ **Scénario 2 — Piège** : N°{_num(surprise)} {_nom(surprise)} peut profiter d'un déroulement favorable.")
        else:
            rep = "Données insuffisantes pour construire les scénarios."

    elif "badge" in q or "signification" in q:
        rep = ("🏷️ **Badges** : D4 = déferré des quatre pieds ; Duo Chaud = couple jockey/entraîneur ; "
               "Spécialiste = aptitude à l'hippodrome ; Rachat = profil à reconsidérer.")

    elif "statistique" in q or "performance" in q or "réussite" in q or "backtest" in q:
        rep = ("📊 Les modules statistiques/backtest sont disponibles côté backend. "
               "Une statistique fiable nécessite l'historique de courses réellement enregistré.")

    elif ("enlève" in q or "retire" in q or "change" in q or "modifie" in q) and precedent:
        rep = (f"🧠 **Consigne prise en compte.** Tu fais référence à : « {precedent} ».\n"
               "La nouvelle demande peut être recalculée à partir des partants disponibles.")

    elif "presse" in q or "consensus" in q:
        cons = presse.get("consensus", [])
        rep = ("📰 **Consensus disponible** : " +
               (", ".join(f"N°{x.get('numero')} {x.get('nom','')}" for x in cons) if cons else "aucune donnée exploitable."))

    elif "météo" in q or "meteo" in q or "piste" in q or "terrain" in q:
        rep = f"🌦️ **Impact météo/piste** : {meteo.get('impact', 'NEUTRE')}."

    else:
        rep = ("Je peux traiter : analyse, Quinté IA indépendant, ticket prudent, "
               "ticket spéculatif, valeur/cotes/Smart Money, comparaison IA/AZ, "
               "base, favoris vulnérables, scénarios, badges, presse, météo/piste et statistiques.")

    return {"status": "success", "question": question, "reponse": rep}
