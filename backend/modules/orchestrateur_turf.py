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


def detecter_intention_large(question: str, historique: list | None = None) -> str:
    q = normaliser(question)
    if not q:
        return "vide"
    if re.search(r"\b(bonjour|salut|hello|bonsoir|coucou|bjr)\b", q) and len(q.split()) <= 8:
        return "salutation"
    if any(x in q for x in ("merci", "je te remercie", "super")) and len(q.split()) <= 8:
        return "merci"

    scores = {}
    for intent, vocab in FAMILLES.items():
        words = set(vocab.split())
        tokens = set(q.split())
        score = len(words & tokens)
        # Bonus sur expressions caractéristiques.
        for expr in vocab.split():
            if len(expr) >= 7 and expr in q:
                score += 1
        scores[intent] = score

    # Priorités explicites : certaines demandes contiennent plusieurs thèmes.
    if "badge" in q or "pastille" in q or "pictogramme" in q or "icone" in q or "signifie" in q:
        return "badges"
    if ("compare" in q or "compar" in q or "versus" in q or "contre" in q or "comparer" in q) and "ticket" in q:
        return "comparaison_tickets"
    if ("compare" in q or "compar" in q or "versus" in q or "contre" in q or "meilleur" in q or "mieux" in q or "difference" in q) and len(nums := extraire_numeros(question, historique)) >= 2:
        return "comparaison_chevaux"
    if any(x in q for x in ("ton pronostic", "ta selection", "ton ticket", "independamment", "independant", "sans az")):
        return "analyse_independante"
    if "premium" in q and any(x in q for x in ("que", "quoi", "difference", "apporte", "fonctionne", "faire")):
        return "premium"
    if scores.get("actualite", 0) and not scores.get("analyse", 0):
        return "actualite"
    if any(x in q for x in ("qui a une chance", "qui a vraiment une chance", "qui peut gagner", "qui peut finir", "qui retenir", "qui retenirais", "qui retiendrais", "le plus interessant", "plus interessant", "meilleur aujourd hui")):
        return "analyse"
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    # Les questions très courtes sur un numéro deviennent une demande cheval.
    if re.search(r"\b(?:le|la|du|sur|avec|pour|numero|n)\s*\d{1,2}\b", q):
        return "cheval"
    return "general"


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
    ctx = dict(contexte or {})
    question_n = normaliser(question)
    # Connaissance turf : uniquement pour les demandes lexicales/explicatives.
    if any(x in question_n for x in ("definition", "signifie", "veut dire", "c est quoi", "qu est ce que")):
        try:
            from .knowledge_turf import expliquer_terme
            termes = [t for t in question_n.split() if len(t) >= 4]
            trouve = None
            for terme in reversed(termes):
                trouve = expliquer_terme(terme)
                if trouve:
                    break
            ctx["connaissance_turf"] = trouve
        except Exception:
            ctx["connaissance_turf"] = None
    # Actualités locales déjà présentes dans le projet, sans appel réseau bloquant.
    if any(x in question_n for x in ("actualite", "news", "nouvelles", "derniere minute")):
        try:
            from .news_turf import resumer_actualite
            ctx["actualites"] = resumer_actualite()
        except Exception:
            ctx["actualites"] = []
    # Couche expert descriptive, additive et non décisionnelle.
    try:
        from .expert_turf import analyser_question_expert
        ctx["expert_accompagnement"] = analyser_question_expert(question, ctx)
    except Exception:
        ctx["expert_accompagnement"] = None
    # Score expert V2 : indicateur complémentaire, distinct du score autonome.
    try:
        from .score_expert_v2 import score_expert
        classement = ((ctx.get("moteur") or {}).get("classement") or [])
        ctx["score_expert_v2"] = {
            str(c.get("numero")): score_expert(
                az=float(c.get("indice_az") or 0),
                forme=float(c.get("forme") or 0),
                marche=0,
                terrain=0,
                jockey=float(c.get("reussite_jockey") or 0),
                presse=0,
            ) for c in classement if isinstance(c, dict) and c.get("numero") is not None
        }
    except Exception:
        ctx["score_expert_v2"] = {}
    # Mémoire et apprentissage : exploitent seulement l'historique fourni à la requête.
    if historique:
        try:
            from .chatbot_memory import generer_contexte_memoire_recent
            ctx["memoire_recent"] = generer_contexte_memoire_recent()
        except Exception:
            ctx["memoire_recent"] = ""
        try:
            from .learning_turf import calculer_indice_confiance
            resultats = []
            for e in historique:
                if isinstance(e, dict) and isinstance(e.get("resultat"), (int, float)):
                    resultats.append(float(e["resultat"]))
            ctx["indice_confiance_apprentissage"] = calculer_indice_confiance(resultats) if resultats else 0
        except Exception:
            ctx["indice_confiance_apprentissage"] = 0
    return ctx
