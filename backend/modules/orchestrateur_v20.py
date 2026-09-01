"""Orchestrateur conversationnel AZ Turf Pro.

Couche additive : elle ne remplace aucun moteur métier existant et ne change
aucune route API. Elle transforme une demande libre en intention, contexte,
modules utiles et réponse exploitable. Les données manquantes sont signalées,
elles ne sont jamais inventées.
"""
from __future__ import annotations
import re
import unicodedata
import math
from typing import Any


def norm(value: Any) -> str:
    text = str(value or "").lower().replace("’", "'")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s%€_-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# Formulations larges : elles servent de signaux sémantiques locaux, pas de
# commandes obligatoires. Plusieurs signaux peuvent coexister dans une même
# demande.
PHRASES = {
    "badges": ("badge", "pastille", "pictogramme", "icone", "symbole", "etiquette", "couleur du cheval"),
    "ticket": ("ticket", "quinte", "quinte", "quarte", "trio", "couple", "combinaison", "selection", "mise", "jouer", "parier"),
    "cotes": ("cote", "cotes", "marche", "mouvement", "baisse", "hausse", "joue", "argent", "value", "valeur", "sous cote", "surcote"),
    "presse": ("presse", "journaliste", "journalistes", "media", "consensus", "avis des journaux", "pronostics presse"),
    "meteo": ("meteo", "pluie", "vent", "terrain", "piste", "sol", "lourd", "souple", "sec", "glissant", "detrempe"),
    "scenario": ("scenario", "rythme", "train", "tactique", "meneur", "animateur", "attentiste", "finisseur", "parcours", "allure"),
    "historique": ("historique", "hier", "avant hier", "precedente", "passee", "resultat", "arrivee", "archive", "souviens", "dernier resultat"),
    "actualite": ("actualite", "actualites", "news", "nouvelle", "nouvelles", "info du jour", "derniere minute", "quoi de neuf", "infos"),
    "premium": ("premium", "abonnement", "version payante", "espace premium", "fonctionnalites avancees"),
    "independant": ("independant", "independante", "sans az", "sans turf pro", "ton propre", "ta propre", "toi meme", "par toi meme", "moteur autonome", "avis autonome"),
    "analyse": ("analyse", "analyser", "avis", "pense", "interessant", "chance", "favori", "base", "retenir", "gagnant", "solide", "fiable", "profil", "forme", "qui peut gagner", "qui a une chance", "meilleur cheval"),
    "aide": ("aide", "capacite", "capacites", "capable", "comment marche", "fonctionnement", "que peux tu", "que sais tu"),
}


def _contains(q: str, phrases) -> bool:
    return any(p in q for p in phrases)


def extract_numbers(question: str, history: list | None = None) -> list[int]:
    q = norm(question)
    # Écarte les années et les heures longues ; les numéros hippiques sont 1-99.
    found = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", q)]
    found = [n for n in found if 1 <= n <= 99]
    if found:
        return list(dict.fromkeys(found))[:10]
    for item in reversed(history or []):
        if not isinstance(item, dict) or str(item.get("role", "")).lower() not in ("user", "utilisateur"):
            continue
        old = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", norm(item.get("content") or item.get("question"))) if 1 <= int(x) <= 99]
        if old:
            return list(dict.fromkeys(old))[:10]
    return []


def detect_intent(question: str, history: list | None = None) -> str:
    q = norm(question)
    if not q:
        return "vide"
    # Les salutations restent conversationnelles et ne doivent pas déclencher
    # l'analyse autonome simplement parce qu'une course est chargée.
    if re.fullmatch(r"(?:bonjour|salut|bonsoir|hello|coucou|bjr)(?:[ !.,-].*)?", q):
        return "salutation"
    numbers = extract_numbers(question, history)
    if _contains(q, PHRASES["badges"]) and any(x in q for x in ("explique", "signifie", "veut dire", "definition", "quoi", "pourquoi", "comprendre", "correspond")):
        return "badges"
    if any(x in q for x in ("compare", "comparaison", "confronte", "versus", "difference entre", "face a", "opposer", "lequel", "laquelle")):
        if _contains(q, ("ticket", "selection", "combinaison", "jeu")) and _contains(q, ("az", "turf pro", "ia", "autonome", "propre", "chatbot")):
            return "comparaison_tickets"
        if len(numbers) >= 2 or any(x in q for x in ("deux chevaux", "deux partants", "ces deux")):
            return "comparaison_chevaux"
        return "comparaison"
    if _contains(q, PHRASES["independant"]):
        return "analyse_independante"
    if _contains(q, ("prudent", "moins de risque", "securise", "securiser", "equilibre", "offensif", "audacieux", "speculatif", "outsider", "grosse cote", "rapport", "mise")) or _contains(q, PHRASES["ticket"]):
        return "ticket"
    # Les demandes composées sont classées par leur action dominante, les autres
    # domaines restant dans le plan multi-module.
    if _contains(q, PHRASES["actualite"]): return "actualite"
    if _contains(q, PHRASES["historique"]): return "historique"
    if _contains(q, PHRASES["cotes"]): return "cotes"
    if _contains(q, PHRASES["meteo"]): return "meteo"
    if _contains(q, PHRASES["presse"]): return "presse"
    if _contains(q, PHRASES["scenario"]): return "scenario"
    if _contains(q, PHRASES["premium"]): return "premium"
    if _contains(q, PHRASES["aide"]): return "aide"
    if numbers and any(x in q for x in ("pourquoi", "avis", "penses", "interessant", "forme", "profil", "retenir", "que vaut", "que vaut il")):
        return "cheval"
    if _contains(q, PHRASES["analyse"]): return "analyse"
    if numbers: return "cheval"
    return "general"


def plan(question: str, history: list | None = None) -> dict:
    q = norm(question); intent = detect_intent(question, history); modules=[]
    def add(*names):
        for n in names:
            if n not in modules: modules.append(n)
    if _contains(q, PHRASES["cotes"]): add("cotes")
    if _contains(q, PHRASES["presse"]): add("presse")
    if _contains(q, PHRASES["meteo"]): add("meteo_piste")
    if _contains(q, PHRASES["scenario"]): add("tactique", "simulation")
    if _contains(q, PHRASES["historique"]): add("historique", "performance")
    if _contains(q, PHRASES["actualite"]): add("actualites")
    if intent in ("analyse", "analyse_independante", "cheval", "comparaison", "comparaison_chevaux", "comparaison_tickets"):
        add("analyse_cheval", "expert", "decision")
    if intent in ("ticket", "comparaison_tickets"):
        add("strategie", "tickets", "simulation")
    if intent == "analyse_independante": add("raisonnement_autonome")
    if intent in ("analyse", "cheval", "comparaison", "comparaison_chevaux"):
        add("cotes", "meteo_piste", "tactique")
    return {"intent": intent, "modules": modules, "numeros": extract_numbers(question, history), "multi_module": len(modules)>1}


def _horse(classement, number):
    return next((c for c in classement if str(c.get("numero")) == str(number)), None)


def _raw_score(c: dict) -> float:
    """Score de lecture autonome. Aucun indice_az/indice_premium/radar AZ."""
    def f(v, default=None):
        try: return float(v)
        except Exception: return default
    vals=[]; weights=[]
    forme=f(c.get("forme")); regularite=f(c.get("regularite"))
    if forme is not None: vals.append(forme*0.30); weights.append(.30)
    if regularite is not None: vals.append(regularite*0.25); weights.append(.25)
    jockey=f(c.get("reussite_jockey"))
    if jockey is not None: vals.append(max(0,min(10,jockey/10))*0.10); weights.append(.10)
    cote=f(c.get("cote_brute", c.get("cote")))
    if cote is not None and cote>0:
        value=max(0,min(10,10/(1+math.log(max(cote,1)))))
        vals.append(value*.10); weights.append(.10)
    perf=c.get("performances") or []
    nums=[]
    if isinstance(perf,list):
        for p in perf:
            try:
                n=float(p); nums.append(n)
            except Exception: pass
    if nums:
        recent=sum(max(0,min(10,11-n)) for n in nums[:5])/min(5,len(nums))
        vals.append(recent*.15); weights.append(.15)
    if not vals: return 0.0
    return round(sum(vals)/sum(weights),2)


def _ticket_list(tickets: Any) -> list[str]:
    if isinstance(tickets, list):
        out=[]
        for x in tickets:
            if isinstance(x, dict): x=x.get("numero") or x.get("num")
            if x is not None: out.append(str(x))
        return out
    if isinstance(tickets, dict):
        for k in ("selection", "quinte", "selection_quinte", "numeros", "chevaux", "bases"):
            if k in tickets:
                r=_ticket_list(tickets[k])
                if r: return r
    return []


def _extract_az_tickets(moteur: dict) -> list[str]:
    tickets=moteur.get("tickets") or {}
    premium=tickets.get("premium") or {}
    gratuit=tickets.get("gratuit") or {}
    return (_ticket_list(premium.get("quinte")) or _ticket_list(premium.get("selection_quinte")) or _ticket_list(gratuit.get("quinte")) or _ticket_list(moteur.get("selection_az")))[:7]


def _format_missing(label: str) -> str:
    return f"{label} : donnée non disponible actuellement. Je ne la remplace pas par une information inventée."


def _response_for_intent(question, contexte, history=None):
    q=norm(question); ctx=contexte or {}; moteur=ctx.get("moteur") or {}
    classement=[c for c in (moteur.get("classement") or moteur.get("chevaux") or []) if isinstance(c,dict)]
    course=ctx.get("course") or {}; numbers=extract_numbers(question,history); intent=detect_intent(question,history)

    if intent == "badges":
        target=_horse(classement,numbers[0]) if numbers else None
        if not target:
            return "🏷️ **Badges AZ Turf Pro**\nLes badges sont des signaux calculés à partir des données du partant (ferrage, aptitude, contexte, etc.). Donnez-moi un numéro si vous voulez l'explication du badge affiché sur ce cheval."
        badges=target.get("badges") if isinstance(target.get("badges"),list) else []
        if not badges: return f"🏷️ Le N°{target.get('numero')} {target.get('nom','')} n'a aucun badge actuellement attribué par le moteur."
        desc={"D4":"quatre pieds déferrés","DP":"configuration de ferrage allégée","DUO_HOT":"signal favorable lié au couple jockey/driver–entraîneur","TRACEE":"aptitude particulière détectée","RACHAT":"profil à reprendre après une contre-performance récente"}
        lines=[]
        for b in badges:
            code=b.get("code","") if isinstance(b,dict) else str(b); label=b.get("libelle",code) if isinstance(b,dict) else str(b)
            lines.append(f"• **{label}** : {desc.get(code,'signal calculé par le moteur à partir des données disponibles')}.")
        return "🏷️ **Badges du N°%s %s**\n%s"%(target.get("numero"),target.get("nom",""),"\n".join(lines))

    if intent == "comparaison_tickets":
        ranked=sorted(classement,key=_raw_score,reverse=True)
        ia=[str(c.get("numero")) for c in ranked if c.get("numero") is not None][:7]
        auto=ctx.get("tickets_autonomes") or {}
        ia=_ticket_list((auto.get("autonome_equilibre") or auto.get("autonome_prudent") or {})) or ia
        az=_extract_az_tickets(moteur)
        if not ia and not az: return _format_missing("Comparaison des tickets")
        common=[x for x in ia if x in az]
        return ("⚔️ **Comparaison analyse autonome / AZ Turf-Pro**\n\n"
                f"🤖 Analyse autonome : **{' - '.join(ia) or 'indisponible'}**\n"
                f"🏆 AZ Turf-Pro : **{' - '.join(az) or 'indisponible'}**\n"
                f"🤝 Convergences : **{' - '.join(common) or 'aucune'}**\n"
                f"🔎 Différences analyse autonome : **{' - '.join(x for x in ia if x not in az) or 'aucune'}**\n"
                f"🔎 Différences AZ : **{' - '.join(x for x in az if x not in ia) or 'aucune'}**\n\n"
                "Le classement autonome est recalculé à partir de variables brutes disponibles ; il ne lit pas l'indice AZ/Premium.")

    if intent == "comparaison_chevaux":
        if len(numbers)<2: return "⚔️ Pour comparer deux chevaux, donnez simplement leurs numéros, par exemple : « entre le 4 et le 7, lequel te paraît le plus intéressant ? »"
        a,b=_horse(classement,numbers[0]),_horse(classement,numbers[1])
        if not a or not b: return "Je ne trouve pas les deux partants demandés dans les données de la course actuelle."
        sa,sb=_raw_score(a),_raw_score(b); winner=a if sa>sb else b if sb>sa else None
        verdict=f"Le N°{winner.get('numero')} {winner.get('nom','')} ressort devant sur les variables brutes disponibles." if winner else "Les deux profils sont très proches sur les données disponibles."
        return (f"⚔️ **Comparaison N°{a.get('numero')} / N°{b.get('numero')}**\n"
                f"N°{a.get('numero')} {a.get('nom','')} : **{sa}/10** • forme {a.get('forme','-')} • cote {a.get('cote','-')}\n"
                f"N°{b.get('numero')} {b.get('nom','')} : **{sb}/10** • forme {b.get('forme','-')} • cote {b.get('cote','-')}\n\n**Verdict :** {verdict}")

    if intent in ("analyse_independante","analyse","cheval"):
        if not classement: return _format_missing("Analyse de course")
        if numbers:
            c=_horse(classement,numbers[0])
            if not c: return f"Je ne trouve pas le N°{numbers[0]} dans les partants actuellement disponibles."
            return (f"🔎 **N°{c.get('numero')} {c.get('nom','')}**\n"
                    f"Forme : **{c.get('forme','-')}** • Régularité : **{c.get('regularite','-')}** • Cote : **{c.get('cote','-')}**\n"
                    f"Jockey/driver : **{c.get('driver') or c.get('jockey') or '-'}** • Entraîneur : **{c.get('entraineur','-')}**\n"
                    f"Score autonome : **{_raw_score(c)}/10**\n"
                    "Ce score autonome ne dépend pas des indices AZ/Premium.")
        ranked=sorted(classement,key=_raw_score,reverse=True)[:7]
        title="🤖 **Mon analyse autonome**" if intent=="analyse_independante" else "📊 **Analyse de la course**"
        lines=[f"{title}",f"Course : **{course.get('reunion','-')}/{course.get('course_numero','-')} — {course.get('hippodrome','-')}**"]
        for i,c in enumerate(ranked,1): lines.append(f"{i}. N°{c.get('numero','-')} **{c.get('nom','')}** — { _raw_score(c) }/10")
        if ranked: lines.append(f"\n🎯 Base autonome : **N°{ranked[0].get('numero')} {ranked[0].get('nom','')}**")
        return "\n".join(lines)

    if intent == "ticket":
        auto=ctx.get("tickets_autonomes") or {}
        mode="autonome_equilibre"
        if _contains(q,("prudent","moins de risque","securise","securiser")): mode="autonome_prudent"
        elif _contains(q,("offensif","audacieux","speculatif","grosse cote","outsider","rapport")): mode="autonome_offensif"
        selected=_ticket_list(auto.get(mode))
        if not selected:
            ranked=sorted(classement,key=_raw_score,reverse=True); size={"autonome_prudent":4,"autonome_equilibre":5,"autonome_offensif":7}[mode]; selected=[str(c.get('numero')) for c in ranked[:size] if c.get('numero') is not None]
        if not selected: return _format_missing("Ticket autonome")
        return f"🎟️ **Ticket {mode.replace('autonome_','')} autonome**\nSélection : **{' - '.join(selected)}**\nBase : **{selected[0]}**\nLe ticket est produit par la voie autonome du chatbot, séparément de l'indice AZ."

    if intent == "cotes":
        rows=((ctx.get("tendances_cotes") or {}).get("resultats") or [])
        if not rows: return _format_missing("Cotes et mouvements de marché")
        rows=sorted(rows,key=lambda x: float(x.get("variation_pct",0) or 0))
        lines=["💰 **Marché / cotes**"]
        for r in rows[:7]: lines.append(f"N°{r.get('numero','-')} {r.get('nom','')} : {r.get('cote_direct','-')} • {r.get('variation_pct',0)} % • {r.get('signal','NEUTRE')}")
        return "\n".join(lines)

    if intent == "meteo":
        m=ctx.get("impact_meteo") or {}; etat=m.get("etat") or (course.get("terrain") if isinstance(course,dict) else None)
        impact=m.get("impact") or "INCONNU"
        return f"🌦️ **Piste / météo**\nÉtat : **{etat or 'non disponible'}**\nImpact détecté : **{impact}**" if etat or impact!="INCONNU" else _format_missing("Piste et météo")

    if intent == "presse":
        p=ctx.get("consensus_presse") or {}; rows=p.get("consensus") or []
        if not rows: return _format_missing("Consensus presse")
        return "📰 **Consensus presse**\n"+"\n".join(f"N°{x.get('numero')} : {x.get('votes',0)} avis" for x in rows[:10])

    if intent == "scenario":
        t=ctx.get("tactique") or {}; r=t.get("rythme") or {}
        return (f"🛣️ **Scénario de course**\n{t.get('scenario','Scénario non déterminable avec les données disponibles.')}\n"
                f"Animateurs probables : {', '.join(map(str,r.get('animateurs_probables') or [])) or 'non identifiés'}\n"
                f"Finisseurs probables : {', '.join(map(str,r.get('finisseurs_probables') or [])) or 'non identifiés'}")

    if intent == "actualite":
        data=ctx.get("actualites")
        if not data:
            try:
                from .actualites_hippiques import recuperer_actualites
                data=recuperer_actualites(8)
            except Exception: data=None
        items=(data or {}).get("actualites") if isinstance(data,dict) else data
        if not items: return _format_missing("Actualités hippiques")
        return "📰 **Actualités disponibles**\n"+"\n".join(f"• {x.get('titre','Information')} — {x.get('source','source')}" for x in items[:8] if isinstance(x,dict))

    if intent == "historique":
        try:
            from learning import lire_historique
            h=lire_historique() or []
            if not h: return "📚 Aucun historique enregistré sur le serveur actuellement."
            e=h[-1]; c=e.get('course') or {}
            arr=e.get('arrivee') or e.get('arrivee_officielle') or []
            return (f"📚 **Dernière course enregistrée**\n{c.get('date',e.get('date','-'))} — {c.get('hippodrome',e.get('hippodrome','-'))} — {c.get('reunion',e.get('reunion','-'))}/{c.get('course_numero',e.get('course_numero','-'))}\n"
                    f"Sélection : {' - '.join(map(str,e.get('selection_az') or [])) or 'non enregistrée'}\n"
                    f"Arrivée : {' - '.join(map(str,arr)) if arr else 'non disponible'}")
        except Exception: return _format_missing("Historique")

    if intent == "premium":
        return "💎 **Premium**\nPremium doit donner accès aux fonctions réellement disponibles : analyse approfondie, tickets Premium, assistant conversationnel, données complémentaires et suivi des performances lorsque les sources sont disponibles."
    if intent == "aide":
        return "🏇 **Vous pouvez me parler librement.** Analysez une course, un cheval, deux chevaux, les cotes, la piste, la tactique, la presse, les actualités, l'historique, les badges, un ticket ou demandez une comparaison entre mon analyse autonome et AZ Turf-Pro. Vous n'avez pas besoin d'utiliser une commande exacte."
    if intent == "general" and len(q.split()) <= 12:
        return "Je vous écoute. Décrivez simplement ce que vous voulez savoir sur la course ou un cheval ; je sélectionnerai les modules utiles à partir de votre demande."
    return None


def respond(question: str, contexte: dict, history: list | None = None) -> dict | None:
    result=_response_for_intent(question,contexte,history)
    if result is None: return None
    intent=detect_intent(question,history)
    return {"status":"success","question":question,"reponse":result,"intent":intent,"plan":plan(question,history),"source":"orchestrateur_local_v21"}
