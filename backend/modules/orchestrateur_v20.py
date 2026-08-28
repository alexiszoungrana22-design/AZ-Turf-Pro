"""Orchestrateur conversationnel V20 pour AZ Turf Pro.

Couche de compréhension locale et d'orchestration dynamique. Elle ne remplace
aucun moteur métier : elle choisit les capacités à utiliser et conserve le
contexte. Aucun service IA externe n'est requis.
"""
from __future__ import annotations
import re
import unicodedata
from typing import Any


def norm(s: Any) -> str:
    s = str(s or "").lower().replace("’", "'")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


INTENTS = {
    "badges": ["badge", "badges", "pastille", "pictogramme", "icone", "symbole", "etiquette"],
    "comparaison_tickets": ["compare", "comparaison", "difference", "versus", "contre", "opposer"],
    "comparaison_chevaux": ["compare", "comparaison", "contre", "versus", "lequel", "laquelle", "mieux", "meilleur"],
    "analyse_independante": ["independant", "independante", "sans az", "sans turf pro", "ton propre", "ta propre", "toi meme", "par toi meme", "moteur autonome"],
    "ticket": ["ticket", "quinte", "quarte", "trio", "combinaison", "selection", "jeu", "mise", "pari", "prudent", "securise", "equilibre", "offensif", "outsider"],
    "cotes": ["cote", "cotes", "marche", "mouvement", "hausse", "baisse", "value", "sous cote", "argent"],
    "presse": ["presse", "journaliste", "journalistes", "media", "consensus", "avis presse"],
    "meteo": ["meteo", "pluie", "vent", "terrain", "piste", "lourd", "souple", "sec", "glissant"],
    "scenario": ["scenario", "rythme", "train", "tactique", "meneur", "anime", "attentiste", "parcours"],
    "historique": ["historique", "hier", "avant hier", "precedente", "passee", "resultat", "arrivee", "archive", "souviens"],
    "actualite": ["actualite", "actualites", "news", "nouvelle", "nouvelles", "info du jour", "derniere minute", "quoi de neuf"],
    "premium": ["premium", "abonnement", "version payante", "fonctionnalites avancees"],
    "aide": ["aide", "capacite", "capacites", "capable", "peux tu", "sais tu", "comment marche", "fonctionnement"],
    "analyse": ["analyse", "analyser", "avis", "pense", "interessant", "chance", "favori", "base", "retenir", "gagnant", "solide", "fiable", "profil", "forme"],
}


def nums(question: str, history: list | None = None) -> list[int]:
    found = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", norm(question))]
    if found:
        return list(dict.fromkeys(found))[:10]
    for item in reversed(history or []):
        if not isinstance(item, dict):
            continue
        if str(item.get("role", "")).lower() not in ("user", "utilisateur"):
            continue
        text = item.get("content") or item.get("question") or ""
        old = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", norm(text))]
        if old:
            return list(dict.fromkeys(old))[:10]
    return []


def _has(q: str, values: list[str]) -> bool:
    return any(v in q for v in values)


def detect_intent(question: str, history: list | None = None) -> str:
    q = norm(question)
    if not q:
        return "vide"
    n = nums(question, history)
    if _has(q, INTENTS["badges"]) and _has(q, ["explique", "signifie", "veut dire", "definition", "quoi", "pourquoi", "comprendre"]):
        return "badges"
    if _has(q, ["compare", "comparaison", "confronte", "versus", "contre", "difference entre", "lequel", "laquelle"]):
        if _has(q, ["ticket", "selection", "combinaison", "jeu"]) and _has(q, ["az", "turf pro", "ia", "autonome", "propre", "chatbot"]):
            return "comparaison_tickets"
        if len(n) >= 2:
            return "comparaison_chevaux"
        return "comparaison"
    if _has(q, INTENTS["analyse_independante"]):
        return "analyse_independante"
    # Demandes de tickets : les contraintes peuvent être exprimées sans le mot ticket.
    if _has(q, ["prudent", "securise", "moins de risque", "sans trop de risque", "equilibre", "offensif", "audacieux", "outsider", "grosse cote", "mise"]):
        return "ticket"
    if _has(q, INTENTS["ticket"]):
        return "ticket"
    # Questions ciblées par numéro : elles héritent de l'intention dominante.
    if _has(q, INTENTS["cotes"]): return "cotes"
    if _has(q, INTENTS["meteo"]): return "meteo"
    if _has(q, INTENTS["presse"]): return "presse"
    if _has(q, INTENTS["scenario"]): return "scenario"
    if _has(q, INTENTS["historique"]): return "historique"
    if _has(q, INTENTS["actualite"]): return "actualite"
    if _has(q, INTENTS["premium"]): return "premium"
    if _has(q, INTENTS["aide"]): return "aide"
    if n and _has(q, ["qui", "quel", "quelle", "pourquoi", "penses", "avis", "interessant", "forme", "profil", "retenir", "chance"]):
        return "cheval"
    if _has(q, INTENTS["analyse"]): return "analyse"
    return "general"


def plan(question: str, history: list | None = None) -> dict:
    q = norm(question)
    intent = detect_intent(question, history)
    modules: list[str] = []
    def add(*names):
        for name in names:
            if name not in modules: modules.append(name)
    if _has(q, INTENTS["cotes"]): add("cotes")
    if _has(q, INTENTS["presse"]): add("presse")
    if _has(q, INTENTS["meteo"]): add("meteo_piste")
    if _has(q, INTENTS["scenario"]): add("tactique", "simulation")
    if _has(q, INTENTS["historique"]): add("historique", "performance")
    if _has(q, INTENTS["actualite"]): add("actualites")
    if intent in ("analyse", "analyse_independante", "cheval", "comparaison", "comparaison_chevaux", "comparaison_tickets"):
        add("analyse_cheval", "expert", "decision")
    if intent in ("ticket", "comparaison_tickets"):
        add("strategie", "tickets", "simulation")
    if intent == "analyse_independante": add("raisonnement_autonome")
    # Une demande de jugement sur une course implique une lecture transversale,
    # même si l'utilisateur n'a cité aucun module technique.
    if intent in ("analyse", "cheval", "comparaison", "comparaison_chevaux"):
        add("cotes", "meteo_piste", "tactique")
    return {"intent": intent, "modules": modules, "numeros": nums(question, history), "multi_module": len(modules) > 1}


def _horse(classement: list[dict], number: int):
    return next((c for c in classement if str(c.get("numero")) == str(number)), None)


def _score(c: dict) -> float:
    def f(v, d=5.0):
        try: return max(0.0, min(10.0, float(v)))
        except Exception: return d
    vals = [f(c.get("forme")), f(c.get("regularite"))]
    radar = c.get("radar") if isinstance(c.get("radar"), dict) else {}
    vals += [f(radar.get(k)) for k in ("distance", "jockey", "classe", "fraicheur") if radar.get(k) is not None]
    try:
        cote = float(c.get("cote"))
        if cote > 0:
            import math
            vals.append(max(0, min(10, 10/(1+math.log(max(cote,1))))) )
    except Exception:
        pass
    return round(sum(vals)/len(vals), 2)


def _ticket_nums(moteur: dict) -> tuple[list[str], list[str]]:
    tickets = moteur.get("tickets") or {}
    def extract(x):
        if isinstance(x, dict):
            for k in ("selection", "numeros", "chevaux", "quinte", "bases"):
                if k in x:
                    return extract(x[k])
        if isinstance(x, list):
            out=[]
            for y in x:
                if isinstance(y, dict): y=y.get("numero") or y.get("num")
                if y is not None: out.append(str(y))
            return out
        return []
    az = extract((tickets.get("premium") or {}).get("quinte")) or extract((tickets.get("gratuit") or {}).get("quinte"))
    if not az: az = [str(x) for x in (moteur.get("selection_az") or [])]
    return az[:7], az


def respond(question: str, contexte: dict, history: list | None = None) -> dict | None:
    """Réponses locales spécialisées. Retourne None pour laisser le moteur
    historique prendre le relais quand les données sont réellement absentes."""
    q = norm(question); intent = detect_intent(question, history)
    ctx = contexte or {}; moteur = ctx.get("moteur") or {}
    classement = [c for c in (moteur.get("classement") or moteur.get("chevaux") or []) if isinstance(c, dict)]
    course = ctx.get("course") or {}; numbers = nums(question, history)
    if intent == "badges":
        descriptions = {
            "D4":"les quatre pieds sont déferrés",
            "DP":"configuration de ferrage allégée indiquée par les données",
            "DUO_HOT":"signal de confiance lié au jockey/driver et/ou à l'entraîneur",
            "TRACEE":"aptitude particulière détectée, notamment sur l'hippodrome",
            "RACHAT":"profil à reprendre après une performance récente défavorable",
        }
        target = _horse(classement, numbers[0]) if numbers else None
        if target:
            badges = target.get("badges") if isinstance(target.get("badges"), list) else []
            if badges:
                lines=[]
                for b in badges:
                    code=b.get("code","") if isinstance(b,dict) else ""
                    label=b.get("libelle",code) if isinstance(b,dict) else str(b)
                    lines.append(f"• **{label}** : {descriptions.get(code, 'signal calculé par le moteur à partir des données disponibles')}.")
                text=f"🏷️ **Badges du N°{target.get('numero')} {target.get('nom','')}**\n"+"\n".join(lines)
            else:
                text=f"🏷️ Le N°{target.get('numero')} {target.get('nom','')} n'a aucun badge attribué sur cette course."
        else:
            text=("🏷️ **Comprendre les badges**\n"
                  "Les badges sont des signaux visuels issus des données du partant. "
                  "D4 concerne le déferrage des quatre pieds ; DUO_HOT signale un contexte favorable jockey/driver–entraîneur ; "
                  "TRACEE indique une aptitude détectée ; RACHAT signale un profil à reprendre. "
                  "Si vous me donnez un numéro, je peux expliquer précisément les badges de ce cheval.")
        return {"status":"success","reponse":text,"intent":"badges","source":"orchestrateur_v20"}

    if intent == "comparaison_tickets":
        ranked=sorted(classement,key=_score,reverse=True)
        ia=[str(c.get("numero")) for c in ranked if c.get("numero") is not None][:7]
        az,_=_ticket_nums(moteur)
        common=[n for n in ia if n in az]; ia_only=[n for n in ia if n not in az]; az_only=[n for n in az if n not in ia]
        if not ia and not az: return None
        text=("⚔️ **Comparaison IA autonome / AZ Turf-Pro**\n\n"
              f"🤖 IA autonome : **{' - '.join(ia) or 'indisponible'}**\n"
              f"🏆 AZ Turf-Pro : **{' - '.join(az) or 'indisponible'}**\n"
              f"🤝 Convergences : **{' - '.join(common) or 'aucune'}**\n"
              f"🔎 IA seulement : **{' - '.join(ia_only) or 'aucun'}**\n"
              f"🔎 AZ seulement : **{' - '.join(az_only) or 'aucun'}**\n\n"
              "L'IA autonome recalcule son classement à partir des variables brutes disponibles ; elle ne réutilise pas l'indice AZ/Premium pour fabriquer son score.")
        return {"status":"success","reponse":text,"intent":intent,"source":"orchestrateur_v20"}

    if intent == "comparaison_chevaux":
        if len(numbers)<2: return {"status":"success","reponse":"Indiquez les deux numéros à comparer, par exemple : « lequel est le plus intéressant entre le 5 et le 7 ? »","intent":intent,"source":"orchestrateur_v20"}
        a,b=_horse(classement,numbers[0]),_horse(classement,numbers[1])
        if not a or not b: return {"status":"success","reponse":"Je ne trouve pas les deux partants demandés dans les données actuellement disponibles.","intent":intent,"source":"orchestrateur_v20"}
        sa,sb=_score(a),_score(b); winner=a if sa>sb else b if sb>sa else None
        verdict=f"Le N°{winner.get('numero')} {winner.get('nom','')} ressort devant sur les données brutes." if winner else "Les deux profils sont très proches sur les données disponibles."
        return {"status":"success","reponse":("⚔️ **Comparaison**\n"
            f"N°{a.get('numero')} {a.get('nom','')} : **{sa}/10** • forme {a.get('forme','-')}/10 • cote {a.get('cote','-')}\n"
            f"N°{b.get('numero')} {b.get('nom','')} : **{sb}/10** • forme {b.get('forme','-')}/10 • cote {b.get('cote','-')}\n\n**Verdict :** {verdict}"),"intent":intent,"source":"orchestrateur_v20"}

    if intent in ("analyse_independante", "analyse", "cheval"):
        if not classement: return None
        if numbers and intent == "cheval":
            c=_horse(classement,numbers[0])
            if c:
                return {"status":"success","reponse":(f"🔎 **N°{c.get('numero')} {c.get('nom','')}**\n"
                    f"Forme **{c.get('forme','-')}/10** • régularité **{c.get('regularite','-')}/10** • cote **{c.get('cote','-')}**\n"
                    f"Jockey/driver : **{c.get('driver') or c.get('jockey') or '-'}** • entraîneur : **{c.get('entraineur','-')}**\n"
                    f"Musique : **{c.get('musique_brute') or c.get('musique') or '-'}**\n"
                    f"Score autonome : **{_score(c)}/10**"),"intent":intent,"source":"orchestrateur_v20"}
        ranked=sorted(classement,key=_score,reverse=True)[:7]
        selection=" - ".join(str(c.get("numero")) for c in ranked if c.get("numero") is not None)
        title="🤖 **Mon analyse autonome**" if intent=="analyse_independante" else "📊 **Analyse de la course**"
        return {"status":"success","reponse":(f"{title}\n"
            f"Course : **{course.get('reunion','-')}/{course.get('course_numero','-')} — {course.get('hippodrome','-')}**\n"
            f"Sélection issue des données disponibles : **{selection or 'indisponible'}**\n\n"
            f"Base : **N°{ranked[0].get('numero')} {ranked[0].get('nom','')}** ({_score(ranked[0])}/10). "
            "Le classement autonome est calculé séparément des indices AZ/Premium."),"intent":intent,"source":"orchestrateur_v20"}

    if intent == "ticket":
        if not classement: return None
        ranked=sorted(classement,key=_score,reverse=True)
        mode="equilibre"
        if _has(q,["prudent","securise","moins de risque"]): mode="prudent"
        elif _has(q,["offensif","audacieux","speculatif","grosse cote","risque"]): mode="offensif"
        size={"prudent":4,"equilibre":5,"offensif":7}[mode]
        sel=[str(c.get("numero")) for c in ranked[:size] if c.get("numero") is not None]
        return {"status":"success","reponse":f"🎟️ **Ticket autonome {mode}**\nSélection : **{' - '.join(sel)}**\nBase : **{sel[0] if sel else '-'}**\nCe ticket provient du classement indépendant du chatbot.","intent":intent,"source":"orchestrateur_v20"}

    if intent == "aide":
        return {"status":"success","reponse":"🏇 Vous pouvez me parler librement : analyse, cheval, comparaison, ticket, cotes, piste, météo, tactique, presse, actualités, historique, badges, stratégie ou comparaison de mon moteur autonome avec AZ Turf-Pro. Vous n'avez pas besoin de connaître une commande précise.","intent":intent,"source":"orchestrateur_v20"}
    return None
