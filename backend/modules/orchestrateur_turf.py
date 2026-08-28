"""Orchestration conversationnelle large d'AZ Turf Pro.

Cette couche ne dépend d'aucun LLM externe. Elle transforme une formulation
naturelle en intention + entités + contexte, puis délègue aux modules locaux.
Elle est volontairement tolérante aux formulations libres et aux synonymes.
"""
from __future__ import annotations
import re
import unicodedata
from typing import Any


def normaliser(texte: str) -> str:
    s = str(texte or "").lower().replace("’", "'")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


FAMILLES = {
    "comparaison": ("compare comparons comparaison face a versus contre difference different mieux meilleur opposer"),
    "ticket": ("ticket selection combinaison quinte quarte trio couple champ reduit jeu jouer mise pari prudent equilibre offensif"),
    "analyse": ("analyse analyser avis opinion pense penses verdict chance chances favori base selection retenir retient interessant interessante fiable solide qui pourrait gagner gagnant gagnante"),
    "cheval": ("cheval partant numero concurrent profil musique performance derniere course jockey driver entraineur"),
    "cotes": ("cote cotes cotee marche marche des paris argent mouvement baisse hausse valeur value sous cote sur cote"),
    "presse": ("presse journaliste media journaux consensus pronostics avis presse"),
    "meteo": ("meteo temps pluie vent terrain piste sol lourd souple bon terrain collant glissant"),
    "scenario": ("scenario rythme train course tactique anime mene devant attentiste sprinteur corde parcours"),
    "historique": ("historique passe passee precedente avant hier hier resultat arrivee archive memoire souvenir"),
    "actualite": ("actualite actualites news nouvelles derniere minute information infos hippique"),
    "badges": ("badge badges pastille pictogramme icone couleur symbole etiquette signification"),
    "premium": ("premium abonnement offre fonctionnalites avancees complet profondeur payant"),
    "aide": ("aide capacites capable faire peux tu sais faire fonctionnement comment marche"),
}


def _tokens_semantiques(q: str):
    return set(normaliser(q).split())


def detecter_intention_large(question: str, historique: list | None = None) -> str:
    """Compréhension large locale : intentions, formulations et contexte.
    Ce n'est pas une liste de commandes : les expressions sont regroupées par
    concepts et peuvent se combiner. Aucun LLM externe n'est requis."""
    q = normaliser(question)
    if not q:
        return "vide"
    nums = extraire_numeros(question, historique)
    # Petites conversations
    if re.search(r"\b(bonjour|salut|hello|bonsoir|coucou|bjr)\b", q) and len(q.split()) <= 10:
        return "salutation"
    if any(x in q for x in ("merci", "je te remercie", "super merci")) and len(q.split()) <= 10:
        return "merci"
    # Concepts à forte priorité, même avec une formulation inhabituelle.
    if any(x in q for x in ("badge", "badges", "pastille", "pictogramme", "icone", "symbole", "couleur du cheval", "etiquette")) and any(x in q for x in ("explique", "signifie", "veut dire", "correspond", "pourquoi", "c est quoi", "quoi", "signification")):
        return "badges"
    if any(x in q for x in ("compare", "comparons", "confronte", "opposer", "face a", "versus", "contre", "difference entre", "entre le", "entre la", "lequel", "laquelle")):
        if any(x in q for x in ("ticket", "selection", "combinaison", "jeu")) and any(x in q for x in ("az", "ia", "autonome", "premium", "propre")):
            return "comparaison_tickets"
        if len(nums) >= 2 or any(x in q for x in ("deux chevaux", "deux partants", "les deux")):
            return "comparaison_chevaux"
        return "comparaison"
    if any(x in q for x in ("sans az", "independamment d az", "independant d az", "ton propre", "ta propre", "ton pronostic", "ta selection", "ton ticket", "moteur autonome", "avis autonome")):
        return "analyse_independante"
    if any(x in q for x in ("premium", "abonnement", "version payante")) and any(x in q for x in ("quoi", "que", "apporte", "difference", "fonction", "capacite", "compris")):
        return "premium"
    if any(x in q for x in ("ticket", "selection", "quinte", "quarte", "trio", "prudent", "equilibre", "offensif", "deux outsiders", "moins de risque")):
        return "ticket"
    # Intentions factuelles
    groups = {
        "actualite": ("actualite", "news", "nouvelles", "derniere minute", "info du jour", "quoi de neuf", "nouveautes"),
        "cotes": ("cote", "cotes", "marche", "argent", "mouvement", "baisse", "hausse", "value", "sous cote"),
        "meteo": ("meteo", "pluie", "vent", "terrain", "piste", "sol", "lourd", "souple", "sec"),
        "presse": ("presse", "journalistes", "media", "consensus", "pronostics presse"),
        "scenario": ("scenario", "rythme", "train", "tactique", "anime", "meneur", "attentiste", "parcours"),
        "historique": ("historique", "hier", "avant hier", "course precedente", "resultat passe", "arrivee passee", "archive", "souviens"),
        "ticket": ("ticket", "selection", "combinaison", "quinte", "quarte", "trio", "jeu", "mise", "pari"),
        "cheval": ("cheval", "partant", "concurrent", "profil", "musique", "jockey", "driver", "entraineur"),
        "analyse": ("analyse", "avis", "pense", "interessant", "chance", "favori", "base", "retenir", "gagnant", "solide", "fiable", "qui peut gagner"),
    }
    scores={k:sum(2 if phrase in q else 1 for phrase in vals if phrase in q) for k,vals in groups.items()}
    # Les demandes ciblées sur un numéro héritent du contexte précédent.
    if nums and not any(v for k,v in scores.items() if k in ("ticket","actualite","historique") and v):
        if any(x in q for x in ("pourquoi", "avis", "penses", "interessant", "forme", "profil", "retenir")):
            return "cheval"
    if scores.get("analyse",0) and any(x in q for x in ("si la piste", "avec la meteo", "avec la cote", "tenir compte", "en tenant compte")):
        return "analyse"
    best=max(scores,key=scores.get)
    if scores[best] > 0:
        return best
    if nums:
        return "cheval"
    return "general"


def planifier_demande(question: str, contexte: dict, historique: list | None = None) -> dict:
    """Produit un plan d'exécution exploitable par l'orchestrateur.
    Une demande peut appeler plusieurs domaines sans que l'utilisateur connaisse
    les noms internes des modules."""
    q=normaliser(question)
    nums=extraire_numeros(question,historique)
    intent=detecter_intention_large(question,historique)
    modules=[]
    def add(*names):
        for n in names:
            if n not in modules: modules.append(n)
    if any(x in q for x in ("cote","cotes","marche","argent","value","mouvement","sous cote")): add("cotes")
    if any(x in q for x in ("presse","journalistes","media","consensus")): add("presse")
    if any(x in q for x in ("meteo","pluie","vent","terrain","piste","sol","lourd","souple")): add("meteo_piste")
    if any(x in q for x in ("scenario","rythme","train","tactique","anime","meneur","attentiste")): add("tactique","simulation")
    if any(x in q for x in ("historique","hier","precedente","resultat passe","archive","souviens")): add("historique","performance")
    if any(x in q for x in ("actualite","news","nouvelles","derniere minute","info du jour")): add("actualites")
    if intent in ("analyse","analyse_independante","cheval","comparaison","comparaison_chevaux") or any(x in q for x in ("qui a une chance","qui peut gagner","favori","plus interessant","interessant","base")): add("analyse_cheval","expert","decision")
    if intent in ("ticket","comparaison_tickets") or any(x in q for x in ("ticket","selection","quinte","prudent","equilibre","offensif","outsider","deux outsiders")): add("strategie","tickets","simulation")
    if intent=="analyse_independante": add("raisonnement_autonome")
    return {"intent":intent,"numeros":nums,"modules":modules,"multi_module":len(modules)>1}

def extraire_numeros(question: str, historique: list | None = None) -> list[int]:
    q = normaliser(question)
    nums = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", q)]
    # Ne pas interpréter une heure ou une date comme cheval si elle est la seule référence.
    nums = list(dict.fromkeys(nums))[:10]
    if nums:
        return nums
    # Reprise du dernier message utilisateur contenant des numéros.
    for e in reversed(historique or []):
        if not isinstance(e, dict):
            continue
        role = str(e.get("role") or "").lower()
        if role not in ("user", "utilisateur"):
            continue
        old = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", normaliser(e.get("content") or e.get("question") or ""))]
        if old:
            return list(dict.fromkeys(old))[:10]
    return []


def trouver_cheval(classement: list[dict], numero: int | str):
    return next((c for c in classement if str(c.get("numero")) == str(numero)), None)


def liste_numeros_ticket(ticket: Any) -> list[str]:
    if isinstance(ticket, list):
        out = []
        for x in ticket:
            if isinstance(x, dict):
                x = x.get("numero") or x.get("num")
            if x is not None:
                out.append(str(x))
        return out
    if isinstance(ticket, dict):
        for key in ("selection", "quinte", "numeros", "chevaux", "bases"):
            if key in ticket:
                return liste_numeros_ticket(ticket[key])
    return []


def extraire_tickets(tickets: dict) -> dict:
    t = tickets or {}
    gratuit = t.get("gratuit") or {}
    premium = t.get("premium") or {}
    return {
        "az_gratuit": liste_numeros_ticket(gratuit.get("quinte")),
        "az_premium": liste_numeros_ticket(premium.get("quinte") or premium.get("selection_quinte")),
        "az_quarte": liste_numeros_ticket(premium.get("quarte")),
    }


def _score_independant_local(c: dict) -> float:
    """Score indépendant basé sur données brutes, sans indice AZ/Premium."""
    def f(v, default=5.0):
        try: return float(v)
        except Exception: return default
    forme = f(c.get("forme"))
    regularite = f(c.get("regularite"))
    jockey = min(10.0, max(0.0, f(c.get("reussite_jockey"), 20.0) / 4.0))
    radar = c.get("radar") if isinstance(c.get("radar"), dict) else {}
    distance = f(radar.get("distance"), 50.0) / 10.0
    experience = min(10.0, f(c.get("nombre_courses"), 25.0) / 5.0)
    cote = f(c.get("cote"), 8.0)
    import math
    cote_score = 5.0 if cote <= 1 else max(0.0, min(10.0, 10.0 / (1 + math.log(max(cote, 1)))))
    return round(forme*.25 + regularite*.20 + jockey*.10 + distance*.12 + experience*.08 + cote_score*.10 + 5*.15, 2)


def _format_cheval(c: dict) -> str:
    num = c.get("numero", "?")
    nom = c.get("nom") or "sans nom"
    return f"N°{num} **{nom}**"


def repondre(question: str, contexte: dict, historique: list | None = None) -> dict | None:
    """Produit une réponse opérationnelle si la demande est turf.

    Retourne None pour laisser l'ancien moteur traiter une demande non couverte.
    """
    intent = detecter_intention_large(question, historique)
    moteur = (contexte or {}).get("moteur") or {}
    classement = [c for c in (moteur.get("classement") or moteur.get("chevaux") or []) if isinstance(c, dict)]
    course = (contexte or {}).get("course") or {}
    nums = extraire_numeros(question, historique)

    if intent == "badges":
        cible = trouver_cheval(classement, nums[0]) if nums else (classement[0] if classement else None)
        if cible:
            badges = cible.get("badges") if isinstance(cible.get("badges"), list) else []
            if not badges:
                return {"status":"success","reponse":f"🏷️ {_format_cheval(cible)} n'a actuellement aucun badge attribué par le moteur sur cette course.","intent":intent,"source":"orchestrateur_local"}
            descriptions = {
                "D4":"Déferré D4 : le cheval court avec les quatre pieds déferrés.",
                "DP":"Déferré : le ferrage indique un équipement allégé selon les données disponibles.",
                "DUO_HOT":"Duo Chaud : signal lié à la réussite du jockey/driver et/ou à la confiance de l'entraîneur.",
                "TRACEE":"Spécialiste : aptitude particulière à l'hippodrome détectée dans les données.",
                "RACHAT":"Rachat : signal de profil intéressant après une performance défavorable récente, sous réserve des données de course.",
            }
            lines=[]
            for b in badges:
                code=b.get("code") if isinstance(b,dict) else ""
                label=b.get("libelle") if isinstance(b,dict) else str(b)
                lines.append(f"• **{label}** — {descriptions.get(code, 'Signal généré par le moteur à partir des données du partant.')}")
            return {"status":"success","reponse":f"🏷️ **Badges de {_format_cheval(cible)}**\n"+"\n".join(lines),"intent":intent,"source":"orchestrateur_local"}

    if intent == "comparaison_tickets":
        # Ticket autonome recalculé sur données brutes.
        ranked = sorted(classement, key=_score_independant_local, reverse=True)
        ia = [str(c.get("numero")) for c in ranked if c.get("numero") is not None][:5]
        azs = extraire_tickets(moteur.get("tickets") or {})
        az = azs["az_premium"] or azs["az_gratuit"]
        if not az and moteur.get("selection_az"):
            az = [str(x) for x in moteur.get("selection_az")[:5]]
        if not ia and not az:
            return {"status":"success","reponse":"⚠️ Je peux comparer les deux tickets dès que les sélections de la course sont disponibles.","intent":intent,"source":"orchestrateur_local"}
        communs=[n for n in ia if n in az]
        divergences=[n for n in ia if n not in az]
        az_only=[n for n in az if n not in ia]
        texte=("⚔️ **Comparaison du ticket autonome et du ticket AZ Turf Pro**\n\n"
               f"🤖 Mon ticket autonome : **{' - '.join(ia) if ia else 'indisponible'}**\n"
               f"🏆 Ticket AZ Turf Pro : **{' - '.join(az) if az else 'indisponible'}**\n"
               f"🤝 Convergences : **{' - '.join(communs) if communs else 'aucune'}**\n"
               f"🔎 Différences côté autonome : **{' - '.join(divergences) if divergences else 'aucune'}**\n"
               f"🔎 Présents chez AZ mais pas dans mon ticket : **{' - '.join(az_only) if az_only else 'aucun'}**\n\n"
               "Mon classement est recalculé séparément à partir des statistiques brutes disponibles ; l'indice AZ/Premium n'est pas utilisé pour le score autonome.")
        return {"status":"success","reponse":texte,"intent":intent,"source":"orchestrateur_local"}

    if intent == "comparaison_chevaux":
        if len(nums) < 2:
            return {"status":"success","reponse":"Donnez-moi les deux numéros à comparer — par exemple « lequel est le plus intéressant entre le 5 et le 7 ? ».","intent":intent,"source":"orchestrateur_local"}
        a,b=trouver_cheval(classement,nums[0]),trouver_cheval(classement,nums[1])
        if not a or not b:
            missing=nums[0] if not a else nums[1]
            return {"status":"success","reponse":f"Je ne trouve pas le N°{missing} dans les partants actuellement disponibles.","intent":intent,"source":"orchestrateur_local"}
        sa,sb=_score_independant_local(a),_score_independant_local(b)
        verdict=_format_cheval(a) if sa>sb else _format_cheval(b) if sb>sa else "les deux profils"
        details=(f"{_format_cheval(a)} : score autonome {sa}/10, forme {a.get('forme','-')}, cote {a.get('cote','-')}.\n"
                 f"{_format_cheval(b)} : score autonome {sb}/10, forme {b.get('forme','-')}, cote {b.get('cote','-')}.\n\n"
                 f"**Verdict : {verdict} ressort devant sur les données brutes disponibles.**")
        return {"status":"success","reponse":"⚔️ **Comparaison**\n"+details,"intent":intent,"source":"orchestrateur_local"}

    # Une question ciblée sur un numéro doit rester ciblée, même si elle contient
    # des mots généraux comme « pense », « avis » ou « intéressant ».
    q_norm = normaliser(question)
    if nums and any(x in q_norm for x in ("cote", "cotes", "marche", "value", "argent", "mouvement")):
        c = trouver_cheval(classement, nums[0])
        if c:
            return {"status":"success","reponse":f"📈 **Cote du N°{nums[0]} {_format_cheval(c).split('**')[-2] if '**' in _format_cheval(c) else c.get('nom','')}** : {c.get('cote','-')}. Tendance : {c.get('tendance_cote') or c.get('tendance') or 'non renseignée'}. Je peux aussi la confronter à sa forme, son profil et sa valeur relative.","intent":"cotes","source":"orchestrateur_local"}

    if intent in ("analyse_independante", "analyse", "favori", "cheval"):
        if not classement:
            return None
        if nums and (intent == "cheval" or (len(nums) == 1 and not any(x in q_norm for x in ("analyse la course", "analyse du quinte", "selection", "quinte")))):
            c=trouver_cheval(classement,nums[0])
            if c:
                badges=c.get("badges") if isinstance(c.get("badges"),list) else []
                labels=[b.get("libelle") for b in badges if isinstance(b,dict) and b.get("libelle")]
                texte=(f"🔎 **{_format_cheval(c)}**\n"
                        f"Forme : **{c.get('forme','-')}/10** • Régularité : **{c.get('regularite','-')}/10** • Cote : **{c.get('cote','-')}**\n"
                        f"Jockey/driver : **{c.get('driver') or c.get('jockey') or '-'}** • Entraîneur : **{c.get('entraineur','-')}**\n"
                        f"Musique : **{c.get('musique_brute') or c.get('musique') or '-'}**"
                        + (f"\n🏷️ Badges : **{', '.join(labels)}**" if labels else ""))
                return {"status":"success","reponse":texte,"intent":intent,"source":"orchestrateur_local"}
        ranked=sorted(classement,key=_score_independant_local,reverse=True)
        top=ranked[:5]
        nums_out=[str(c.get('numero')) for c in top if c.get('numero') is not None]
        prefix="🤖 **Mon analyse autonome**" if intent=="analyse_independante" else "📊 **Analyse de la course**"
        texte=(f"{prefix}\n"
               f"Course : **{course.get('reunion','-')}/{course.get('course_numero','-')} — {course.get('hippodrome','-')}**\n"
               f"Sélection : **{' - '.join(nums_out)}**\n\n"
               f"Base autonome : **N°{top[0].get('numero')} {top[0].get('nom','')}**. "
               f"Derrière : **{' - '.join(nums_out[1:])}**.\n"
               "Le classement autonome est calculé séparément des indices AZ/Premium à partir des statistiques brutes disponibles.")
        return {"status":"success","reponse":texte,"intent":intent,"source":"orchestrateur_local"}

    if intent == "ticket":
        if not classement: return None
        ranked=sorted(classement,key=_score_independant_local,reverse=True)
        mode="equilibre"
        q=normaliser(question)
        if any(x in q for x in ("prudent","sur","securise","moins de risque")): mode="prudent"
        elif any(x in q for x in ("offensif","speculatif","grosse cote","audacieux","risque")): mode="offensif"
        tailles={"prudent":4,"equilibre":5,"offensif":7}
        sel=[str(c.get("numero")) for c in ranked[:tailles[mode]]]
        return {"status":"success","reponse":f"🎟️ **Ticket autonome {mode}**\nSélection : **{' - '.join(sel)}**\nBase : **{sel[0] if sel else '-'}**\nCe ticket est issu du classement indépendant du chatbot.","intent":intent,"source":"orchestrateur_local"}

    if intent == "cotes":
        r=(contexte or {}).get("tendances_cotes") or {}
        lignes=[]
        for x in r.get("resultats",[]) or []:
            if isinstance(x,dict): lignes.append(f"N°{x.get('numero')} {x.get('nom','')} : {x.get('cote_matin','-')} → {x.get('cote_direct','-')} ({x.get('variation_pct',0):+.1f}%)")
        if lignes:
            return {"status":"success","reponse":"📈 **Marché des cotes**\n"+"\n".join(lignes[:12]),"intent":intent,"source":"orchestrateur_local"}
        return {"status":"success","reponse":"📈 Les données de cotes sont disponibles dans le pipeline, mais aucune évolution exploitable n'est enregistrée pour cette course.","intent":intent,"source":"orchestrateur_local"}

    if intent == "presse":
        r=(contexte or {}).get("consensus_presse") or {}
        val=r.get("consensus") or r.get("resultats")
        return {"status":"success","reponse":"📰 **Presse**\n"+str(val if val else "Aucun consensus presse exploitable n'est fourni pour cette course."),"intent":intent,"source":"orchestrateur_local"}

    if intent == "meteo":
        r=(contexte or {}).get("impact_meteo") or {}
        return {"status":"success","reponse":f"🌦️ **Conditions**\nImpact : **{r.get('impact','INCONNU')}**\nDétails : {r.get('details') or r.get('raison') or 'Aucun détail supplémentaire disponible.'}","intent":intent,"source":"orchestrateur_local"}

    if intent == "scenario":
        r=(contexte or {}).get("tactique") or {}
        return {"status":"success","reponse":"🛣️ **Scénario de course**\n"+str(r if r else "Le module tactique est branché mais ne dispose pas de suffisamment de données pour établir un scénario détaillé."),"intent":intent,"source":"orchestrateur_local"}

    if intent == "actualite":
        r=(contexte or {}).get("actualites")
        if r:
            return {"status":"success","reponse":"📰 **Actualités hippiques**\n"+str(r),"intent":intent,"source":"orchestrateur_local"}
        try:
            from .news_turf import resumer_actualite
            r=resumer_actualite()
            return {"status":"success","reponse":"📰 **Actualités hippiques**\n"+str(r),"intent":intent,"source":"orchestrateur_local"}
        except Exception:
            return None

    if intent == "historique":
        try:
            from learning import lire_historique
            h=lire_historique()
            return {"status":"success","reponse":f"📚 **Historique**\n{len(h)} entrée(s) actuellement accessibles par le moteur.","intent":intent,"source":"orchestrateur_local"}
        except Exception:
            return None

    if intent == "aide":
        return {"status":"success","reponse":"🏇 Je comprends les demandes formulées naturellement : analyse, cheval, comparaison, tickets, cotes, presse, météo/piste, scénario, historique, actualités, badges et comparaison entre mon moteur autonome et AZ Turf Pro. Vous n'avez pas besoin d'utiliser une commande précise.","intent":intent,"source":"orchestrateur_local"}

    return None

# --- Enrichissement additionnel : modules d'accompagnement historiques ---
def enrichir_modules_accompagnement(contexte: dict, question: str, historique: list | None = None) -> dict:
    """Orchestre réellement les modules disponibles selon le plan de demande.
    Chaque module est isolé : une panne d'une source ne bloque pas le chatbot."""
    ctx = dict(contexte or {})
    moteur = dict(ctx.get("moteur") or {})
    chevaux = [c for c in (moteur.get("classement") or moteur.get("chevaux") or []) if isinstance(c, dict)]
    course = dict(ctx.get("course") or {})
    plan = planifier_demande(question, ctx, historique)
    ctx["plan_chatbot"] = plan
    def safe(key, fn, default=None):
        try: ctx[key] = fn()
        except Exception as exc:
            ctx[key] = default
            ctx.setdefault("diagnostic_modules", {})[key] = type(exc).__name__
    # Données transversales : elles deviennent disponibles à tous les intents.
    safe("tendances_cotes", lambda: __import__("modules.cotes_history", fromlist=["analyser_tendances_cotes"]).analyser_tendances_cotes({"chevaux": chevaux}), {"status":"indisponible","resultats":[]})
    safe("consensus_presse", lambda: __import__("modules.pronos_presse", fromlist=["analyser_consensus_presse"]).analyser_consensus_presse({"info_course":course,"chevaux":chevaux,"pronostics":course.get("pronostics_presse") or course.get("presse") or []}), {"status":"indisponible","consensus":[]})
    safe("impact_meteo", lambda: __import__("modules.meteo_piste", fromlist=["analyser_impact_terrain"]).analyser_impact_terrain({"info_course":course,"meteo":course.get("meteo"),"terrain":course.get("terrain") or course.get("etat_piste")}), {"status":"indisponible","impact":"INCONNU"})
    safe("expert_accompagnement", lambda: __import__("modules.expert_turf", fromlist=["analyser_question_expert"]).analyser_question_expert(question,ctx), None)
    safe("expert_marche", lambda: __import__("modules.expert_turf", fromlist=["analyser_marche"]).analyser_marche(ctx), None)
    safe("expert_performance", lambda: __import__("modules.expert_turf", fromlist=["analyser_performance"]).analyser_performance(ctx), None)
    safe("expert_conditions", lambda: __import__("modules.expert_turf", fromlist=["analyser_conditions"]).analyser_conditions(ctx), None)
    safe("expert_valeur", lambda: __import__("modules.expert_turf", fromlist=["analyser_valeur"]).analyser_valeur(ctx), None)
    safe("profils_chevaux", lambda: __import__("modules.pronostiqueur_engine", fromlist=["analyser_profils_chevaux"]).analyser_profils_chevaux(chevaux), [])
    profils=ctx.get("profils_chevaux") or []
    safe("synthese_pronostiqueur", lambda: __import__("modules.pronostiqueur_engine", fromlist=["generer_synthese"]).generer_synthese(profils), None)
    safe("tactique", lambda: __import__("modules.tactique_course_engine", fromlist=["analyser_scenario_course"]).analyser_scenario_course(chevaux), None)
    safe("rythme_course", lambda: __import__("modules.tactique_course_engine", fromlist=["analyser_rythme_course"]).analyser_rythme_course(chevaux), None)
    # Raisonnement autonome : calcul indépendant des indices AZ/Premium.
    safe("raisonnement_autonome", lambda: __import__("modules.autonomous_reasoning", fromlist=["analyze_independently"]).analyze_independently(ctx), {"independent":True,"horses":[]})
    try:
        from .autonomous_reasoning import make_tickets, compare_to_az
        ctx["tickets_autonomes"] = make_tickets(ctx["raisonnement_autonome"])
        ctx["comparaison_autonome_az"] = compare_to_az(ctx["raisonnement_autonome"],ctx)
    except Exception: ctx["tickets_autonomes"]={}
    # Modules de tickets/risque si un ticket est demandé ou si une comparaison est demandée.
    if plan["intent"] in ("ticket","comparaison_tickets","analyse_independante") or "ticket" in plan["modules"]:
        try:
            from .strategie_pari_engine import definir_profil_parieur, construire_ticket_strategique, evaluer_risque_ticket
            selection=[h.get("numero") for h in (ctx.get("raisonnement_autonome",{}).get("horses") or [])[:7] if h.get("numero") is not None]
            ctx["strategies"]={}
            for mode in ("prudent","equilibre","offensif"):
                tk=construire_ticket_strategique(selection,mode)
                ctx["strategies"][mode]={"ticket":tk,"risque":evaluer_risque_ticket(tk)}
        except Exception: ctx["strategies"]={}
    # Connaissance et actualités : formulation libre, pas seulement "définition".
    if plan["intent"] in ("general","badges","premium") or any(x in normaliser(question) for x in ("signifie","veut dire","explique","comment marche")):
        try:
            from .knowledge_turf import expliquer_terme
            for terme in reversed(normaliser(question).split()):
                if len(terme)>=4 and (res:=expliquer_terme(terme)):
                    ctx["connaissance_turf"]=res; break
        except Exception: pass
    if plan["intent"]=="actualite" or any(x in normaliser(question) for x in ("actualite","news","nouvelles")):
        safe("actualites", lambda: __import__("modules.news_turf", fromlist=["resumer_actualite"]).resumer_actualite(), [])
    if historique:
        safe("memoire_recent", lambda: __import__("modules.chatbot_memory", fromlist=["generer_contexte_memoire_recent"]).generer_contexte_memoire_recent(), "")
    return ctx

