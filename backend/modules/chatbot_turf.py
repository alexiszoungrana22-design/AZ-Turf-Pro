"""AZ TURF PRO — Assistant conversationnel IA
Un pronostiqueur hippique et analyste, pas un chatbot à commandes :
la question est envoyée telle quelle à un modèle de langage (Claude ou
OpenAI), avec le contexte complet de la course, pour un vrai raisonnement
et une conversation naturelle sur n'importe quelle formulation.

Configuration (variables d'environnement, sur Render → Environment) :
  ANTHROPIC_API_KEY   clé Claude (prioritaire par défaut)
  OPENAI_API_KEY      clé OpenAI (utilisée en secours, ou en priorité si
                       AI_PROVIDER=openai)
  AI_PROVIDER         "anthropic" (défaut) ou "openai"

Si aucune des deux clés n'est configurée, ou si les deux appels échouent
(réseau, quota...), l'assistant retombe sur une réponse minimale par
mots-clés pour ne jamais laisser le client sans réponse.
"""

import os
import json
import httpx

# Modules d'orchestration complémentaires : ils enrichissent le moteur existant
# sans modifier ses scores ni ses routes API.
try:
    from modules.intent_orchestrator import analyser as _planifier_demande
    from modules.value_analysis import analyser_valeur as _analyser_valeur, resume_valeur as _resume_valeur
    from modules.race_scenarios import resume_scenarios as _resume_scenarios
    from modules.arbitre_ia_az import resume as _resume_arbitre
except Exception:
    _planifier_demande = _analyser_valeur = _resume_valeur = _resume_scenarios = _resume_arbitre = None

# Branchement en bloc des modules d'accompagnement historiques, jusqu'ici non
# reliés à l'API : orchestrateur_turf.py (enrichissement réel des modules
# satellites : cotes, presse, météo, expert_turf, pronostiqueur_engine,
# tactique_course_engine, autonomous_reasoning, strategie_pari_engine,
# knowledge_turf, news_turf, chatbot_memory) et orchestrateur_v20.py (réponse
# locale de secours qui consomme ce même contexte enrichi). Purement additif :
# aucun score AZ, aucune route existante, aucun comportement actuel n'est modifié.
try:
    from modules.orchestrateur_turf import enrichir_modules_accompagnement as _enrichir_accompagnement_bloc
except Exception:
    _enrichir_accompagnement_bloc = None

try:
    from modules.orchestrateur_v20 import respond as _repondre_orchestrateur_v20
except Exception:
    _repondre_orchestrateur_v20 = None

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").strip().lower()

CLAUDE_MODEL = "claude-sonnet-5"
OPENAI_MODEL = "gpt-4o-mini"

TIMEOUT_SECONDES = 25


# =====================================
# CONSTRUCTION DU CONTEXTE COURSE
# =====================================

def _resume_course(contexte: dict) -> str:
    course = (contexte or {}).get("course", {}) or {}
    lignes = [
        f"Réunion/Course : {course.get('reunion', '-')} / "
        f"{course.get('course_numero', '-')} — {course.get('course', '-')}",
        f"Hippodrome : {course.get('hippodrome', '-')}",
        f"Discipline : {course.get('discipline', '-')} sur "
        f"{course.get('distance_course', '-')} m",
        f"Date / heure de départ : {course.get('date', '-')} "
        f"{course.get('heure_depart', '-')}",
        f"Allocation : {course.get('allocation', '-')}",
    ]
    non_partants = course.get("non_partants") or []
    if non_partants:
        lignes.append(f"Non-partants : {', '.join(str(n) for n in non_partants)}")

    complement_galop = (contexte or {}).get("complement_france_galop")
    if complement_galop:
        lignes.append(str(complement_galop))

    return "\n".join(lignes)


def _resume_classement(contexte: dict, limite: int = 20) -> str:
    moteur = (contexte or {}).get("moteur", {}) or {}
    classement = moteur.get("classement", []) or []
    lignes = []
    for cheval in classement[:limite]:
        if not isinstance(cheval, dict):
            continue
        driver = cheval.get("driver") or cheval.get("conducteur") or cheval.get("pilote") or cheval.get("jockey") or "-"
        tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"
        forme = cheval.get("forme")
        regularite = cheval.get("regularite")
        confiance = cheval.get("confiance")

        ligne = (
            f"N°{cheval.get('numero', '?')} {cheval.get('nom', '?')} "
            f"({cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}) — "
            f"jockey/driver : {driver}, "
            f"entraîneur : {cheval.get('entraineur', '-')} | "
            f"cote {cheval.get('cote', '-')} (tendance {tendance}), "
            f"indice AZ {cheval.get('indice_az', '-')}, "
            f"indice Premium {cheval.get('indice_premium', '-')}"
        )
        if confiance is not None:
            ligne += f", confiance {confiance}%"
        ligne += (
            f" | musique : {cheval.get('musique_brute', '-')}"
        )
        if forme is not None:
            ligne += f" (forme {forme}/10"
            if regularite is not None:
                ligne += f", régularité {regularite}/10"
            ligne += ")"
        ligne += (
            f", gains carrière : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}, "
            f"corde : {cheval.get('corde', '-')}, "
            f"ferrage : {cheval.get('deferre', '-')}"
        )

        # Statistiques avancées, jusque-là jamais exploitées par le chatbot
        jockey_pct = cheval.get("reussite_jockey")
        conf_entraineur = cheval.get("confiance_entraineur")
        hippo_fav = cheval.get("hippodromes_favoris")
        dist_pref = cheval.get("distance_predilection")
        jours_repos = cheval.get("jours_depuis_derniere_course")
        variation_pct = cheval.get("variation_cote_pct")
        radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
        badges = cheval.get("badges") if isinstance(cheval.get("badges"), list) else []

        extras = []
        if jockey_pct is not None:
            extras.append(f"réussite jockey {jockey_pct}%")
        if conf_entraineur is not None:
            extras.append(f"confiance entraîneur {conf_entraineur}")
        if hippo_fav:
            extras.append(f"hippodromes favoris : {hippo_fav}")
        if dist_pref is not None:
            extras.append(f"distance de prédilection {dist_pref}m")
        if jours_repos is not None:
            extras.append(f"{jours_repos}j depuis la dernière course")
        if variation_pct is not None and variation_pct != 0:
            sens = "baisse (argent qui rentre)" if variation_pct < 0 else "hausse (argent qui sort)"
            extras.append(f"cote en {sens} de {abs(variation_pct)}%")
        if extras:
            ligne += " | " + ", ".join(extras)

        if radar:
            ligne += (
                f" | Radar/100 — forme:{radar.get('forme','-')}, "
                f"distance:{radar.get('distance','-')}, jockey:{radar.get('jockey','-')}, "
                f"classe:{radar.get('classe','-')}, fraîcheur:{radar.get('fraicheur','-')}"
            )
        if badges:
            libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
            if libelles:
                ligne += f" | Badges : {', '.join(libelles)}"

        lignes.append(ligne)
    return "\n".join(lignes) if lignes else "Aucun classement disponible."


def _resume_tickets(contexte: dict) -> str:
    moteur = (contexte or {}).get("moteur", {}) or {}
    tickets = moteur.get("tickets", {}) or {}
    try:
        return json.dumps(tickets, ensure_ascii=False, default=str)
    except Exception:
        return "Tickets indisponibles."


def _construire_system_prompt(contexte: dict) -> str:
    return (
        "Tu es AZ Turf Pro, un pronostiqueur hippique professionnel, "
        "reconnu et confiant, qui échange avec les abonnés d'une "
        "application de pronostics Quinté+. Tu n'es pas un menu de "
        "commandes : tu comprends et réponds naturellement à n'importe "
        "quelle question, même formulée différemment de ce qui est prévu, "
        "et tu maîtrises toutes les statistiques disponibles (cotes, "
        "tendances de cote, indices AZ et Premium, driver/jockey, "
        "entraîneur, musique, forme, régularité, corde, ferrage, gains "
        "carrière).\n\n"
        "Règles :\n"
        "- Réponds en français, avec l'assurance d'un vrai professionnel "
        "du turf qui connaît sa course sur le bout des doigts — direct, "
        "net, sans formules d'hésitation inutiles (\"je pense que\", "
        "\"peut-être\" à éviter sauf incertitude réelle sur la donnée).\n"
        "- Appuie-toi uniquement sur les données de course fournies "
        "ci-dessous. N'invente jamais de cote, de nom de cheval, de "
        "jockey ou de résultat qui n'y figure pas.\n"
        "- Si une information précise demandée n'est pas dans les "
        "données (ex. un historique détaillé non fourni), dis-le "
        "honnêtement plutôt que de l'inventer — mais formule ça comme "
        "une limite ponctuelle, pas comme une excuse générale.\n"
        "- Utilise activement TOUTES les statistiques à ta disposition : "
        "la musique et la forme récente, le driver, l'entraîneur, la "
        "corde, le ferrage, les tendances de cote (argent qui rentre ou "
        "sort) sont autant d'arguments à mobiliser, pas seulement "
        "l'indice AZ brut.\n"
        "- Argumente, compare, nuance, donne un vrai avis tranché "
        "d'analyste — pas seulement réciter des chiffres.\n"
        "- Reste concis (quelques phrases ou un court paragraphe), sauf "
        "si la question demande explicitement plus de détail.\n\n"
        "=== DONNÉES DE LA COURSE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO (toutes statistiques disponibles) ===\n"
        f"{_resume_classement(contexte)}\n\n"
        "=== TICKETS GÉNÉRÉS ===\n"
        f"{_resume_tickets(contexte)}\n"
    )


def _historique_pour_ia(historique: list, limite: int = 12) -> list:
    """Normalise l'historique envoyé par le frontend (chatbot.js) vers un
    format role/content compatible avec les deux API."""
    messages = []
    for entree in (historique or [])[-limite:]:
        if not isinstance(entree, dict):
            continue
        role = entree.get("role") or ("user" if entree.get("question") else "assistant")
        contenu = entree.get("content") or entree.get("question") or entree.get("reponse") or ""
        if not contenu:
            continue
        role = "assistant" if role in ("assistant", "bot", "ia") else "user"
        messages.append({"role": role, "content": str(contenu)})
    return messages


# =====================================
# APPELS AUX MODÈLES
# =====================================

def _appeler_claude(system_prompt: str, messages: list, question: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY non configurée.")

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": messages + [{"role": "user", "content": question}],
    }
    reponse = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=TIMEOUT_SECONDES,
    )
    if reponse.status_code >= 400:
        raise RuntimeError(f"Claude {reponse.status_code} : {reponse.text[:500]}")
    data = reponse.json()
    morceaux = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    texte = "".join(morceaux).strip()
    if not texte:
        raise RuntimeError("Réponse Claude vide.")
    return texte


def _appeler_openai(system_prompt: str, messages: list, question: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY non configurée.")

    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "system", "content": system_prompt}]
        + messages
        + [{"role": "user", "content": question}],
        "max_tokens": 1000,
    }
    reponse = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=TIMEOUT_SECONDES,
    )
    if reponse.status_code >= 400:
        raise RuntimeError(f"OpenAI {reponse.status_code} : {reponse.text[:500]}")
    data = reponse.json()
    texte = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    if not texte:
        raise RuntimeError("Réponse OpenAI vide.")
    return texte


# =====================================
# REPLI SANS IA (aucune clé configurée / échec des deux appels)
# =====================================

# =====================================
# MOTEUR D'ANALYSE RÉEL (raisonnement sur les données, sans IA externe)
# =====================================

def _indice(cheval: dict) -> float:
    try:
        return float(cheval.get("indice_az") or cheval.get("indice_premium") or 0)
    except (TypeError, ValueError):
        return 0.0


def _cote(cheval: dict) -> float:
    try:
        return float(cheval.get("cote") or 0)
    except (TypeError, ValueError):
        return 0.0


def _score_ia_independant(cheval: dict) -> float:
    """Score IA 0-10 VOLONTAIREMENT INDÉPENDANT de l'indice AZ/Premium
    (n'utilise jamais indice_az ni indice_premium). Recalcule sa propre
    opinion à partir des statistiques brutes, pour offrir une vraie
    seconde lecture — c'est ce qui permet une comparaison "Ticket IA"
    vs "Ticket AZ Turf Pro" qui ait un sens (deux calculs distincts).
    """
    import math as _math

    forme = float(cheval.get("forme") or 5.0)
    regularite = float(cheval.get("regularite") or 5.0)

    nb_courses = cheval.get("nombre_courses")
    experience = min(10.0, float(nb_courses) / 5.0) if nb_courses else 5.0

    gains_bruts = cheval.get("gains_carriere") or cheval.get("gains") or 0
    try:
        gains_par_course = float(gains_bruts) / max(1, int(nb_courses or 1))
        gains_score = min(10.0, max(0.0, gains_par_course / 1000.0))
    except (TypeError, ValueError):
        gains_score = 5.0

    reussite = cheval.get("reussite_jockey")
    jockey_score = min(10.0, float(reussite) / 4.0) if reussite is not None else 5.0

    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    distance_score = float(radar.get("distance")) / 10.0 if radar.get("distance") is not None else 5.0
    terrain_score = 5.0  # pas de donnée terrain fiable et systématique disponible

    cote = _cote(cheval)
    cote_confiance = 5.0 if cote <= 1 else max(0.0, min(10.0, 10.0 / (1.0 + _math.log(cote))))

    score = (
        forme * 0.25 + regularite * 0.20 + distance_score * 0.12 + terrain_score * 0.08 +
        jockey_score * 0.10 + experience * 0.07 + gains_score * 0.08 + cote_confiance * 0.10
    )
    return round(max(0.0, min(10.0, score)), 2)


def _trouver_cheval(classement: list, numero: str):
    return next((c for c in classement if str(c.get("numero")) == str(numero)), None)


def _analyser_favori(classement: list) -> str:
    if not classement:
        return "Aucune analyse de course n'est disponible pour le moment."
    top = classement[0]
    ecart = None
    if len(classement) >= 2:
        ecart = round(_indice(top) - _indice(classement[1]), 2)

    if ecart is not None and ecart >= 5:
        confiance = "Il se détache nettement du reste du peloton — un favori solide."
    elif ecart is not None and ecart >= 1.5:
        confiance = "Il devance ses poursuivants avec une marge correcte, mais sans être hors de portée."
    elif ecart is not None:
        confiance = f"L'écart avec le N°{classement[1].get('numero')} n'est que de {ecart} points — course ouverte, ce favori peut être renversé."
    else:
        confiance = "Seul cheval réellement analysé sur cette course."

    badges = top.get("badges") if isinstance(top.get("badges"), list) else []
    libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
    argument_badges = f" Arguments supplémentaires : {', '.join(libelles)}." if libelles else ""

    jours_repos = top.get("jours_depuis_derniere_course")
    note_repos = ""
    if isinstance(jours_repos, (int, float)):
        if jours_repos > 90:
            note_repos = f" Attention : {int(jours_repos)} jours sans courir, la fraîcheur est incertaine."
        elif jours_repos <= 30:
            note_repos = f" Repos idéal ({int(jours_repos)}j) pour être au top."

    return (
        f"🎯 **Favori AZ Turf Pro** : N°{top.get('numero')} **{top.get('nom')}** "
        f"(Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')}). {confiance}"
        f"{argument_badges}{note_repos}"
    )


def _analyser_vulnerables(classement: list) -> str:
    if len(classement) < 2:
        return "Pas assez de chevaux analysés pour juger d'une vulnérabilité."

    vulnerables = []
    for i, cheval in enumerate(classement[:5]):
        if i == len(classement) - 1:
            continue
        suivant = classement[i + 1]
        ecart = _indice(cheval) - _indice(suivant)
        cote_elevee = _cote(cheval) >= 6
        if ecart < 1.5 or cote_elevee:
            raisons = []
            if ecart < 1.5:
                raisons.append(f"talonné de près par le N°{suivant.get('numero')} (écart de {round(ecart, 2)} pts)")
            if cote_elevee:
                raisons.append(f"une cote qui reste élevée ({cheval.get('cote')})")
            vulnerables.append(f"- N°{cheval.get('numero')} **{cheval.get('nom')}** : {', '.join(raisons)}.")

    if not vulnerables:
        return "Aucun favori ne semble particulièrement vulnérable sur cette course — le classement paraît net."
    return "⚠️ **Favoris à surveiller** :\n" + "\n".join(vulnerables)


def _comparer_chevaux(classement: list, num_a: str, num_b: str) -> str:
    a = _trouver_cheval(classement, num_a)
    b = _trouver_cheval(classement, num_b)
    if not a or not b:
        manquant = num_a if not a else num_b
        return f"Je ne trouve pas le numéro {manquant} dans le classement de cette course."

    rang_a = classement.index(a) + 1
    rang_b = classement.index(b) + 1
    diff = round(_indice(a) - _indice(b), 2)

    if diff > 0:
        verdict = f"N°{num_a} **{a.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_a} vs {rang_b})."
    elif diff < 0:
        verdict = f"N°{num_b} **{b.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_b} vs {rang_a})."
    else:
        verdict = "Les deux chevaux sont à égalité d'indice — un vrai coin de table."

    return (
        f"**N°{num_a} {a.get('nom')}** (indice {a.get('indice_az', '-')}, cote {a.get('cote', '-')}) "
        f"vs **N°{num_b} {b.get('nom')}** (indice {b.get('indice_az', '-')}, cote {b.get('cote', '-')}) : {verdict}"
    )


def _classement_ia(classement: list) -> list:
    """Reclasse les chevaux selon le score IA indépendant (pas
    l'indice AZ) — c'est ce classement que les tickets IA utilisent."""
    copie = [dict(c) for c in classement]
    for c in copie:
        c["_ia_score"] = _score_ia_independant(c)
    return sorted(copie, key=lambda c: c["_ia_score"], reverse=True)


def _ticket_prudent(classement: list) -> str:
    """Ne retient que les valeurs sûres selon le score IA indépendant :
    les mieux notés ET les plus réguliers, sans aucun outsider."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire un ticket prudent."
    classe = _classement_ia(classement)
    surs = sorted(classe, key=lambda c: (-c["_ia_score"], -float(c.get("regularite") or 0), _cote(c)))[:5]
    nums = [str(c.get("numero")) for c in surs]
    return (
        "🛡️ **Ticket IA PRUDENT (indépendant)** : " + " - ".join(nums) + "\n"
        f"Base IA : N°{surs[0].get('numero')} {surs[0].get('nom', '')} (score IA {surs[0]['_ia_score']}/10).\n"
        "Priorité : forme, régularité — aucun outsider, calcul séparé de l'indice AZ."
    )


def _ticket_speculatif(classement: list) -> str:
    """Privilégie les outsiders à cote élevée dont le score IA
    indépendant reste correct — recherche du gros rapport."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire un ticket spéculatif."
    classe = _classement_ia(classement)
    outsiders = [c for c in classe if _cote(c) >= 12]
    outsiders = sorted(outsiders, key=lambda c: -c["_ia_score"])[:3]
    solides = [c for c in classe if c not in outsiders][:2]
    combinaison = (outsiders + solides)[:5]
    nums = [str(c.get("numero")) for c in combinaison]
    outsiders_txt = (
        "\n".join(f"• N°{c.get('numero')} {c.get('nom','')} — cote {_cote(c)} — score IA {c['_ia_score']}/10" for c in outsiders)
        if outsiders else "• Aucun outsider à cote ≥ 12 avec des données suffisantes."
    )
    return (
        "🎲 **Ticket IA SPÉCULATIF (indépendant, risqué)** : " + " - ".join(nums) + "\n\n"
        f"Outsiders réellement retenus :\n{outsiders_txt}\n\n"
        "Accepte davantage de risque — ne recopie pas le ticket AZ Turf Pro."
    )


def _ticket_mix(classement: list) -> str:
    """Équilibre selon le score IA indépendant : les meilleures valeurs
    sûres + 1-2 outsiders, sans tout miser sur un seul profil."""
    if len(classement) < 4:
        return "Pas assez de chevaux analysés pour construire un ticket mixte."
    classe = _classement_ia(classement)
    surs = classe[:3]
    surs_numeros = {c.get("numero") for c in surs}
    outsiders = [c for c in classe if _cote(c) >= 8 and c.get("numero") not in surs_numeros][:2]
    if not outsiders:
        outsiders = [c for c in classe if c.get("numero") not in surs_numeros][-2:]
    combinaison = surs + outsiders
    nums = [str(c.get("numero")) for c in combinaison]
    return (
        "⚖️ **Ticket IA MIX (équilibré, indépendant)** : " + " - ".join(nums) + "\n"
        "Combine les meilleures valeurs sûres (score IA) et 1 à 2 outsiders "
        "pour doser risque et régularité — calcul séparé de l'indice AZ."
    )


def _generer_scenarios(classement: list) -> str:
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire des scénarios."

    favori, second, troisieme = classement[0], classement[1], classement[2]
    outsiders = [c for c in classement if _cote(c) >= 10]
    outsider = outsiders[0] if outsiders else classement[-1]

    return (
        "🛤️ **Deux scénarios possibles** :\n\n"
        f"**Scénario logique** : le favori N°{favori.get('numero')} **{favori.get('nom')}** confirme sa "
        f"place, devant N°{second.get('numero')} **{second.get('nom')}** et N°{troisieme.get('numero')} "
        f"**{troisieme.get('nom')}** — un ordre proche du classement AZ Turf Pro.\n\n"
        f"**Scénario surprise** : N°{outsider.get('numero')} **{outsider.get('nom')}** "
        f"(cote {outsider.get('cote', '-')}) crée la sensation et vient bousculer le favori, "
        "profitant d'un faux rythme ou d'une méforme du leader."
    )


def _fiche_cheval(cheval: dict) -> str:
    driver = cheval.get("driver") or cheval.get("conducteur") or cheval.get("pilote") or cheval.get("jockey") or "-"
    forme = cheval.get("forme")
    regularite = cheval.get("regularite")
    tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"

    fiche = (
        f"**N°{cheval.get('numero')} {cheval.get('nom')}** — "
        f"{cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}\n"
        f"- Jockey/Driver : {driver} (réussite {cheval.get('reussite_jockey', '-')}%)\n"
        f"- Entraîneur : {cheval.get('entraineur', '-')} (confiance {cheval.get('confiance_entraineur', '-')})\n"
        f"- Cote : {cheval.get('cote', '-')} (tendance {tendance}) | Indice AZ : {cheval.get('indice_az', '-')} | "
        f"Indice Premium : {cheval.get('indice_premium', '-')}\n"
        f"- Musique (forme récente) : {cheval.get('musique_brute', '-')}"
    )
    if forme is not None:
        fiche += f" — forme {forme}/10"
        if regularite is not None:
            fiche += f", régularité {regularite}/10"
    fiche += (
        f"\n- Gains de carrière : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))} | "
        f"Nombre de courses : {cheval.get('nombre_courses', '-')}\n"
        f"- Corde : {cheval.get('corde', '-')} | Ferrage : {cheval.get('deferre', '-')}\n"
        f"- Distance de prédilection : {cheval.get('distance_predilection', '-')}m | "
        f"Repos : {cheval.get('jours_depuis_derniere_course', '-')} jours\n"
        f"- Hippodromes favoris : {cheval.get('hippodromes_favoris', '-')}"
    )

    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    if radar:
        fiche += (
            f"\n- Radar/100 : forme {radar.get('forme', '-')}, distance {radar.get('distance', '-')}, "
            f"jockey {radar.get('jockey', '-')}, classe {radar.get('classe', '-')}, "
            f"fraîcheur {radar.get('fraicheur', '-')}"
        )

    badges = cheval.get("badges") if isinstance(cheval.get("badges"), list) else []
    libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
    if libelles:
        fiche += f"\n- Badges : {', '.join(libelles)}"

    return fiche


def _points_forts_faibles(cheval: dict) -> str:
    """Analyse réelle des points forts/faibles à partir du radar 5
    axes déjà calculé par le moteur — pas de texte générique."""
    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    if not radar:
        return (f"N°{cheval.get('numero')} **{cheval.get('nom')}** : pas de radar "
                f"détaillé disponible pour cette course.")

    libelles = {
        "forme": "la forme récente", "distance": "l'aptitude à la distance du jour",
        "jockey": "le duo jockey/entraîneur", "classe": "le niveau de classe",
        "fraicheur": "la fraîcheur (repos)",
    }
    valides = {k: v for k, v in radar.items() if isinstance(v, (int, float))}
    if not valides:
        return f"N°{cheval.get('numero')} **{cheval.get('nom')}** : radar incomplet."

    meilleur = max(valides, key=valides.get)
    pire = min(valides, key=valides.get)

    return (
        f"N°{cheval.get('numero')} **{cheval.get('nom')}** :\n"
        f"✅ Point fort : {libelles.get(meilleur, meilleur)} ({valides[meilleur]}/100)\n"
        f"⚠️ Point faible : {libelles.get(pire, pire)} ({valides[pire]}/100)"
    )


# =====================================
# RECHERCHE INDÉPENDANTE EN DIRECT (PMU.fr)
# =====================================
#
# Contrairement au contexte habituel (calculé une fois par le moteur
# AZ au début de la conversation), cette fonction relance un VRAI
# appel réseau vers PMU.fr au moment précis de la question, pour les
# demandes qui portent explicitement sur l'évolution en direct
# (cotes, dernière minute). Best-effort : échec toujours silencieux,
# ne casse jamais la conversation si PMU.fr est indisponible.

# =====================================
# ANALYSE RÉTROSPECTIVE (courses passées + arrivées réelles)
# =====================================
#
# S'appuie sur learning.py / historique_az.json, déjà alimenté
# automatiquement par engine.py à chaque /api/analyse. Permet de
# vraiment expliquer si la sélection AZ a fonctionné ou non, en
# comparant la sélection au classement d'arrivée officiel PMU.
#
# ⚠️ LIMITE CONNUE (déjà documentée dans api.py) : si l'hébergement
# Render ne dispose pas d'un disque persistant, ce fichier peut être
# remis à zéro à chaque redéploiement — l'historique ne survivrait
# alors pas dans le temps. À vérifier concrètement sur ton plan
# Render si cette fonctionnalité te semble incomplète en usage réel.

def _analyser_historique() -> str | None:
    try:
        from learning import lire_historique

        entrees = [e for e in lire_historique() if isinstance(e, dict)]
        avec_arrivee = [e for e in entrees if e.get("arrivee")]
        if not avec_arrivee:
            return None

        derniere = avec_arrivee[-1]
        course = derniere.get("course") or {}
        arrivee = derniere.get("arrivee") or []
        selection_az = derniere.get("selection_az") or []
        favori = derniere.get("favori") or {}

        gagnant_reel = str(arrivee[0]) if arrivee else None
        numero_favori = str(favori.get("numero")) if favori.get("numero") is not None else None

        lignes = [
            f"📋 **Dernière course analysée** : {course.get('hippodrome', '-')} "
            f"({course.get('date', '-')}, {course.get('reunion', '-')}/{course.get('course_numero', '-')})",
            f"Notre sélection : {' - '.join(str(n) for n in selection_az[:7])}",
            f"Arrivée réelle : {' - '.join(str(n) for n in arrivee[:7])}" if arrivee else "Arrivée réelle : non disponible pour le moment.",
        ]

        if gagnant_reel and numero_favori:
            if gagnant_reel == numero_favori:
                lignes.append(
                    f"✅ Notre favori (N°{numero_favori}) a remporté la course — "
                    "sélection gagnante confirmée."
                )
            elif gagnant_reel in [str(n) for n in selection_az[:7]]:
                rang = [str(n) for n in selection_az[:7]].index(gagnant_reel) + 1
                lignes.append(
                    f"⚠️ Le vrai gagnant (N°{gagnant_reel}) figurait dans notre sélection "
                    f"(en position {rang}), mais pas en tête — le favori N°{numero_favori} "
                    "n'a pas confirmé sa cote de sortie."
                )
            else:
                lignes.append(
                    f"❌ Le gagnant réel (N°{gagnant_reel}) ne figurait pas dans notre "
                    f"sélection — notre favori N°{numero_favori} n'était pas le bon choix "
                    "sur cette course, un imprévu (forme du jour, tactique de course, "
                    "terrain) a rebattu les cartes."
                )

        return "\n".join(lignes)
    except Exception:
        return None


def _analyser_course_passee(question: str) -> str | None:
    """Regarde l'historique réel (learning.py) pour répondre sur une
    course passée : sa sélection, et — si l'arrivée officielle a été
    récupérée entre-temps — pourquoi ça a marché ou pas, en comparant
    concrètement les numéros joués aux numéros arrivés."""
    import re as _re
    try:
        from learning import lire_historique
    except Exception:
        return None

    q = question.lower()
    if not any(k in q for k in ["hier", "course passée", "course passee", "dernière course",
                                  "derniere course", "pourquoi ça a marché", "pourquoi ca a marche",
                                  "pourquoi ça n'a pas marché", "résultat", "resultat", "arrivée", "arrivee"]):
        return None

    try:
        historique = lire_historique() or []
    except Exception:
        return None
    if not historique:
        return "Aucun historique de course n'est encore enregistré."

    # "hier" ou pas de date précisée -> la plus récente course TERMINÉE (avec arrivée connue)
    entrees_avec_arrivee = [e for e in historique if isinstance(e, dict) and e.get("arrivee")]
    if not entrees_avec_arrivee:
        return ("Aucune course passée n'a encore d'arrivée officielle enregistrée — "
                "je ne peux pas encore analyser de résultat.")

    entree = entrees_avec_arrivee[-1]  # la plus récente avec arrivée connue
    arrivee = [str(n) for n in entree.get("arrivee", [])]
    selection = [str(n) for n in (entree.get("selection_az") or [])]
    hippodrome = entree.get("hippodrome", "-")
    date = entree.get("date", "-")

    if not selection:
        return f"L'arrivée du {date} à {hippodrome} était {' - '.join(arrivee)}, mais aucune sélection n'a été enregistrée pour comparer."

    touches = [n for n in selection if n in arrivee]
    manques = [n for n in selection if n not in arrivee]
    nb_touches = len(touches)

    if nb_touches >= 3:
        verdict = "Un bon résultat : la sélection a largement recoupé l'arrivée réelle."
    elif nb_touches >= 1:
        verdict = "Un résultat partiel : quelques chevaux de la sélection sont sortis, pas tous."
    else:
        verdict = "Aucun cheval de la sélection n'est sorti dans l'arrivée — la course a déjoué le classement AZ."

    return (
        f"📋 **Course du {date} — {hippodrome}**\n"
        f"Arrivée officielle : {' - '.join(arrivee)}\n"
        f"Sélection AZ jouée : {' - '.join(selection)}\n"
        f"Chevaux sortis parmi la sélection : {', '.join(touches) if touches else 'aucun'} "
        f"({nb_touches}/{len(selection)})\n"
        f"{verdict}"
    )


def _analyser_course_demain(question: str, course_actuelle: dict) -> str | None:
    """Tente de récupérer en direct le programme PMU du lendemain.
    Best-effort : PMU ne publie pas toujours les partants aussi loin
    à l'avance ; échoue silencieusement si l'info n'existe pas encore."""
    q = question.lower()
    if "demain" not in q:
        return None

    try:
        from pmu_source import charger_course_pmu
        from datetime import datetime, timedelta

        demain = (datetime.now() + timedelta(days=1)).strftime("%d%m%Y")
        course_demain = charger_course_pmu(demain)

        if not course_demain or not isinstance(course_demain, dict) or not course_demain.get("chevaux"):
            return ("Le programme PMU de demain n'est pas encore publié ou disponible "
                    "à cet instant — réessayez plus tard, généralement il sort la veille "
                    "au soir.")

        nb = len(course_demain.get("chevaux", []))
        hippodrome = course_demain.get("hippodrome", "-")
        return (
            f"📅 **Programme PMU de demain trouvé** : {hippodrome}, {nb} partants "
            f"annoncés. L'analyse AZ Turf Pro complète (indices, tickets) n'est "
            f"générée qu'au moment où la course devient celle du jour — je peux "
            f"seulement confirmer sa disponibilité pour l'instant."
        )
    except Exception:
        return ("Je n'ai pas pu vérifier le programme de demain à l'instant "
                "(PMU.fr indisponible ou pas encore publié).")


def _rafraichir_cotes_pmu_direct(course_reference: dict) -> str | None:
    try:
        from pmu_source import charger_course_pmu

        date = course_reference.get("date")
        reunion = course_reference.get("reunion")
        course_numero = course_reference.get("course_numero")

        course_fraiche = charger_course_pmu(date, reunion, course_numero)
        if not course_fraiche or not isinstance(course_fraiche, dict):
            return None

        chevaux = course_fraiche.get("chevaux", [])
        if not chevaux:
            return None

        lignes = []
        for cheval in chevaux[:10]:
            if not isinstance(cheval, dict):
                continue
            tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"
            lignes.append(
                f"N°{cheval.get('numero', '?')} {cheval.get('nom', '?')} : "
                f"cote actuelle {cheval.get('cote', '-')} (tendance {tendance})"
            )
        if not lignes:
            return None

        return "[Cotes PMU.fr rafraîchies en direct]\n" + "\n".join(lignes)
    except Exception:
        return None


def _extraire_tickets(tickets: dict) -> dict:
    """Normalise la structure RÉELLE de tickets renvoyée par
    quinte.py (generer_tickets_az), documentée ici une bonne fois
    pour toutes pour éviter les erreurs de structure récurrentes :

    tickets = {
      "gratuit": {
        "quinte": [7 numéros],
        "deux_sur_quatre": [4 numéros],
        "couple_place": [2 numéros],
      },
      "premium": {
        "selection_quinte": [8 numéros],
        "quinte": [6 numéros],
        "quarte": [5 numéros],
        "trio": [3 numéros],
        "couple_gagnant_place": [[a,b],[a,c],[b,c]],
        "champ_reduit": {"format", "bases", "complements", "disponible"},
        "ticket_derniere_minute": {"selection", "joker", "format"},
      }
    }
    Tous les numéros sont des CHAÎNES BRUTES (pas des objets/dicts).
    """
    tickets = tickets or {}
    gratuit = tickets.get("gratuit") or {}
    premium = tickets.get("premium") or {}

    def _liste(valeur):
        return valeur if isinstance(valeur, list) else []

    return {
        "quinte_gratuit": _liste(gratuit.get("quinte")),
        "deux_sur_quatre": _liste(gratuit.get("deux_sur_quatre")),
        "couple_place_gratuit": _liste(gratuit.get("couple_place")),
        "selection_quinte_premium": _liste(premium.get("selection_quinte")),
        "quinte_premium": _liste(premium.get("quinte")),
        "quarte_premium": _liste(premium.get("quarte")),
        "trio_premium": _liste(premium.get("trio")),
        "couple_gagnant_place": _liste(premium.get("couple_gagnant_place")),
        "champ_reduit": premium.get("champ_reduit") if isinstance(premium.get("champ_reduit"), dict) else {},
        "derniere_minute": premium.get("ticket_derniere_minute") if isinstance(premium.get("ticket_derniere_minute"), dict) else {},
    }


def _reponse_plan_local(question: str, contexte: dict) -> str | None:
    """Réponses locales structurées pour les demandes composées.
    Elles servent de moteur de secours quand aucune API IA externe n'est configurée.
    """
    plan = (contexte or {}).get("plan_chatbot") or {}
    classement = ((contexte or {}).get("moteur") or {}).get("classement") or []
    nums = [str(x) for x in plan.get("chevaux") or []]
    q = question.lower()

    if not classement:
        return None

    # Les demandes pédagogiques explicites sont prioritaires sur une intention
    # générique « analyse indépendante ».
    if "badges" in (plan.get("intentions") or []):
        return ("🏷️ **Guide des badges AZ Turf Pro**\n"
                "• **D4** : cheval déferré des quatre pieds.\n"
                "• **Duo Chaud 🔥** : association jockey/entraîneur signalée en réussite.\n"
                "• **Spécialiste 🎯** : aptitude particulière détectée par les données disponibles.\n"
                "• **Rachat ⚡** : profil à surveiller après une performance décevante.\n\n"
                "Les badges sont des signaux complémentaires : ils ne remplacent pas l'analyse globale.")

    # Comparaison de deux chevaux : plusieurs critères, pas uniquement l'indice AZ.
    if plan.get("intentions") and "comparaison_chevaux" in plan["intentions"] and len(nums) >= 2:
        a = _trouver_cheval(classement, nums[0]); b = _trouver_cheval(classement, nums[1])
        if not a or not b: return None
        def f(c,k,d=5):
            try: return float(c.get(k) if c.get(k) is not None else d)
            except (TypeError,ValueError): return float(d)
        sa = 0.30*f(a,'forme')+0.22*f(a,'regularite')+0.15*f(a,'distance')+0.13*f(a,'jockey_score')+0.10*f(a,'terrain')+0.10*f(a,'experience')
        sb = 0.30*f(b,'forme')+0.22*f(b,'regularite')+0.15*f(b,'distance')+0.13*f(b,'jockey_score')+0.10*f(b,'terrain')+0.10*f(b,'experience')
        meilleur = a if sa >= sb else b
        autre = b if meilleur is a else a
        raisons=[]
        for k,label in [('forme','forme'),('regularite','régularité'),('distance','distance'),('jockey_score','jockey/driver')]:
            va,vb=f(meilleur,k),f(autre,k)
            if va-vb >= 1: raisons.append(f"{label} ({va:g} contre {vb:g})")
        return (f"⚔️ **Duel N°{a.get('numero')} / N°{b.get('numero')}**\n"
                f"Je donne l'avantage au **N°{meilleur.get('numero')} {meilleur.get('nom')}**. "
                f"Score autonome indicatif : {max(sa,sb):.2f}/10 contre {min(sa,sb):.2f}/10. "
                + ("Les critères qui font la différence : " + ", ".join(raisons) + "." if raisons else "Les profils sont très proches : la cote et le déroulement peuvent départager les deux."))

    if "analyse_independante" in (plan.get("intentions") or []):
        ia = sorted(classement, key=lambda c: __import__('modules.value_analysis', fromlist=['score_independant']).score_independant(c), reverse=True)
        top = ia[:5]
        if not top: return None
        return ("🤖 **Mon analyse indépendante**\n"
                + " — ".join(f"{i+1}. N°{c.get('numero')} {c.get('nom')}" for i,c in enumerate(top))
                + "\n\nCette hiérarchie est calculée séparément des indices AZ/Premium à partir des données brutes disponibles.")

    if "valeur" in (plan.get("intentions") or []):
        try: return "💰 **Analyse de valeur**\n" + _resume_valeur(classement)
        except Exception: return None

    if "scenarios" in (plan.get("intentions") or []):
        try: return "🛤️ **Scénarios possibles**\n" + _resume_scenarios(classement, (contexte or {}).get("course"))
        except Exception: return None

    if "actualites" in (plan.get("intentions") or []):
        return None  # laisse la logique existante utiliser la source d'actualités

    return None


def _reponse_secours(question: str, contexte: dict) -> str:
    import re as _re

    q = question.lower().strip()
    moteur = (contexte or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})
    course = (contexte or {}).get("course", {}) or {}

    plan_response = _reponse_plan_local(question, contexte)
    if plan_response:
        return plan_response

    # --- Comparaison "Ticket IA" (indépendant) vs "Ticket AZ Turf Pro" ---
    if "compar" in q and any(k in q for k in ["az turf", "az", "premium", "ticket ia", "l'ia", "ia et"]):
        classe_ia = _classement_ia(classement)
        ticket_ia = [str(c.get("numero")) for c in classe_ia[:5]]
        tk_tmp = _extraire_tickets(tickets)
        ticket_az = tk_tmp["selection_quinte_premium"] or tk_tmp["quinte_premium"] or tk_tmp["quinte_gratuit"]
        if not ticket_az and classement:
            ticket_az = [str(c.get("numero")) for c in classement[:5]]
            az_label = "classement AZ (proxy, aucun ticket généré disponible)"
        else:
            az_label = "ticket AZ Turf Pro"
        return (
            "⚔️ **Comparaison Ticket IA (indépendant) / Ticket AZ Turf Pro**\n\n"
            f"🤖 Ticket IA : **{' - '.join(ticket_ia)}**\n"
            f"🏆 {az_label} : **{' - '.join(ticket_az) if ticket_az else 'non disponible'}**\n\n"
            "Les deux sélections sont calculées séparément : l'IA n'utilise jamais "
            "l'indice AZ, elle recalcule sa propre opinion à partir des statistiques brutes."
        )

    # --- Comparaison entre deux profils de ticket (prudent/spéculatif/mix/gratuit) ---
    if "compar" in q and "ticket" in q:
        profils_cites = []
        if any(k in q for k in ["prudent", "sûr", "sécurisé"]):
            profils_cites.append(("Prudent", _ticket_prudent(classement)))
        if any(k in q for k in ["spéculat", "speculat", "risqué", "risque", "audacieux"]):
            profils_cites.append(("Spéculatif", _ticket_speculatif(classement)))
        if any(k in q for k in ["mix", "équilibré", "equilibre"]):
            profils_cites.append(("Mix", _ticket_mix(classement)))
        if "premium" in q:
            tk_tmp = _extraire_tickets(tickets)
            if tk_tmp["quinte_premium"]:
                profils_cites.append(("Quinté Premium", "💎 " + " - ".join(tk_tmp["quinte_premium"])))
        if "gratuit" in q:
            tk_tmp = _extraire_tickets(tickets)
            if tk_tmp["quinte_gratuit"]:
                profils_cites.append(("Quinté Gratuit", "💡 " + " - ".join(tk_tmp["quinte_gratuit"])))

        if len(profils_cites) >= 2:
            texte = "🔍 **Comparaison de tickets**\n\n"
            for nom, contenu in profils_cites[:2]:
                texte += f"**{nom}** :\n{contenu}\n\n"
            return texte.strip()

        return ("Pour comparer, précisez deux profils parmi : prudent, spéculatif, mix, "
                "Quinté gratuit ou Quinté Premium — par exemple \"compare le ticket "
                "prudent et le ticket spéculatif\".")

    # --- Analyse de valeur (probabilité modèle vs cote implicite) ---
    if any(k in q for k in ["value", "valeur", "sous-coté", "sous cote", "sous-cote"]):
        import math as _math
        classe_ia = _classement_ia(classement)
        candidats = []
        for c in classe_ia:
            cote = _cote(c)
            if cote >= 8:
                implicite = 1.0 / cote
                proba_modele = max(0.02, min(0.35, 0.02 + (c["_ia_score"] / 10.0) * 0.22))
                ecart = proba_modele - implicite
                candidats.append((ecart, c, proba_modele, implicite))
        candidats.sort(key=lambda x: x[0], reverse=True)
        if not candidats:
            return "Aucun cheval à cote suffisamment élevée (≥8) pour une analyse de valeur sur cette course."
        lignes = [
            f"• N°{c.get('numero')} {c.get('nom','')} — cote {cote:.1f} — proba. modèle {pm*100:.1f}% — "
            f"implicite {pi*100:.1f}% — écart {ecart*100:+.1f} pts"
            for ecart, c, pm, pi in candidats[:5]
            for cote in [_cote(c)]
        ]
        return (
            "💰 **Meilleures valeurs (probabilité modèle vs cote implicite)**\n" +
            "\n".join(lignes) +
            "\n\n⚠️ L'écart est un indicateur du modèle, pas une probabilité garantie."
        )

    # --- Tickets par profil de risque (prudent / spéculatif / mix) ---
    if any(k in q for k in ["prudent", "sûr", "sur ", "sécurisé", "securise", "sans risque"]):
        return _ticket_prudent(classement)
    if any(k in q for k in ["spéculat", "speculat", "risqué", "risque", "audacieux", "gros rapport"]):
        return _ticket_speculatif(classement)
    if any(k in q for k in ["mix", "équilibré", "equilibre", "équilibre"]):
        return _ticket_mix(classement)

    # --- Course passée : sélection vs arrivée réelle ---
    reponse_passe = _analyser_course_passee(question)
    if reponse_passe:
        return reponse_passe

    # --- Course de demain (best-effort PMU) ---
    reponse_demain = _analyser_course_demain(question, course)
    if reponse_demain:
        return reponse_demain

    # --- Recherche indépendante en direct : cotes/dernière minute ---
    if any(k in q for k in ["cote a boug", "cote a change", "evolution", "évolution", "en direct", "temps réel", "temps reel", "à jour", "a jour", "actualise", "actualisé"]):
        rafraichi = _rafraichir_cotes_pmu_direct(course)
        if rafraichi:
            return "🔄 " + rafraichi
        return ("Je n'ai pas pu récupérer une mise à jour en direct depuis PMU.fr à "
                "l'instant. Voici les dernières données connues à la place.\n\n"
                + _analyser_favori(classement))

    # --- Analyse rétrospective : dernière course, arrivée réelle ---
    if any(k in q for k in ["ça a marché", "ca a marche", "résultat", "resultat", "arrivée", "arrivee", "pourquoi ça n'a pas marché", "pourquoi ca n'a pas marche", "course précédente", "course precedente", "dernière course", "derniere course", "bilan"]):
        analyse = _analyser_historique()
        if analyse:
            return analyse
        return ("Aucune course passée avec une arrivée connue n'est disponible pour "
                "le moment — soit aucune analyse précédente n'a été enregistrée, soit "
                "l'arrivée officielle n'a pas encore pu être récupérée.")

    # --- Limite connue : course de demain ---
    if "demain" in q and any(k in q for k in ["course", "analyse", "analyser"]):
        return ("Je ne peux pas encore analyser la course de demain — cette "
                "fonctionnalité dépend d'une donnée supplémentaire non encore "
                "branchée (le programme PMU du lendemain). Je peux en revanche "
                "analyser la course du jour en cours, ou revenir sur les "
                "précédentes avec leur résultat réel.")

    # --- Recherche indépendante en direct : terrain/piste (France Galop) ---
    if any(k in q for k in ["terrain", "piste", "état du sol", "etat du sol", "souple", "lourd", "bon terrain"]):
        try:
            from france_galop_source import obtenir_complement_france_galop
            complement = obtenir_complement_france_galop(course.get("hippodrome", ""), course.get("discipline", ""))
        except Exception:
            complement = None
        if complement:
            return "🔄 " + complement
        return ("Je n'ai pas d'information à jour sur l'état du terrain pour cette "
                "course pour le moment.")

    # --- Salutations ---
    if any(k in q for k in ["bonjour", "salut", "bonsoir", "hello", "coucou"]):
        return ("👋 Bonjour ! Je suis AZ Turf Pro, votre pronostiqueur hippique. "
                "Je peux analyser le favori, repérer les favoris vulnérables, "
                "comparer deux chevaux, proposer des scénarios de course, "
                "expliquer la position d'un cheval précis, donner le meilleur "
                "duo ou la sélection Quinté. Posez votre question !")

    # --- Comparaison de deux chevaux, ex. "compare le 3 et le 7" ---
    numeros_cites = _re.findall(r"\b(\d{1,2})\b", q)
    if len(numeros_cites) >= 2 and any(k in q for k in ["compar", " ou ", "vs", "mieux que", "contre"]):
        return _comparer_chevaux(classement, numeros_cites[0], numeros_cites[1])

    # --- Favoris vulnérables ---
    if any(k in q for k in ["vulnérable", "vulnerable", "fragile", "battable", "renverser", "se méfier", "se mefier", "méfier"]):
        return _analyser_vulnerables(classement)

    # --- Scénarios de course ---
    if "scénario" in q or "scenario" in q:
        return _generer_scenarios(classement)

    # --- Points forts / points faibles d'un cheval (radar) ---
    if numeros_cites and any(k in q for k in ["point fort", "points fort", "point faible", "points faible", "atout", "faiblesse", "avantage", "handicap de"]):
        cheval = _trouver_cheval(classement, numeros_cites[0])
        if cheval:
            return _points_forts_faibles(cheval)
        return f"Je ne trouve pas le numéro {numeros_cites[0]} dans le classement de cette course."

    # --- Statistiques précises d'un cheval : jockey, musique, gains, corde... ---
    if numeros_cites and any(k in q for k in ["jockey", "driver", "entraineur", "entraîneur", "musique", "forme", "gains", "corde", "ferrage", "déferré", "deferre", "âge", "age", "fiche", "stat", "monte", "pilote", "qui monte"]):
        cheval = _trouver_cheval(classement, numeros_cites[0])
        if cheval:
            return _fiche_cheval(cheval)
        return f"Je ne trouve pas le numéro {numeros_cites[0]} dans le classement de cette course."

    # --- Cheval précis, ex. "pourquoi enlever/exclure le 4 ?" ---
    if numeros_cites and any(k in q for k in ["pourquoi", "enlever", "exclure", "éliminer", "eliminer", "sortir", "numero", "numéro", "cheval", "n°"]):
        numero = numeros_cites[0]
        cheval = _trouver_cheval(classement, numero)
        if cheval:
            rang = classement.index(cheval) + 1
            if rang <= 3:
                jugement = "Il fait partie du trio de tête — un choix cohérent."
            else:
                jugement = "Son indice est nettement en retrait par rapport aux chevaux devant lui, ce qui justifie sa position."
            return (
                f"N°{numero} **{cheval.get('nom')}** est classé **{rang}ᵉ** par AZ Turf Pro "
                f"(Indice AZ {cheval.get('indice_az', '-')}, cote {cheval.get('cote', '-')}). "
                f"{jugement}"
            )
        return f"Je ne trouve pas le numéro {numero} dans le classement de cette course."

    tk = _extraire_tickets(tickets)

    # --- Meilleur duo / couplé gagnant-placé ---
    if any(k in q for k in ["duo", "couple", "couplé", "gagnant placé", "gagnant/placé"]):
        if tk["couple_gagnant_place"]:
            paire = tk["couple_gagnant_place"][0]
            if isinstance(paire, list) and len(paire) >= 2:
                return f"🤝 **Meilleur duo (Couplé Gagnant/Placé Premium)** : N°{paire[0]} - N°{paire[1]}."
        if len(tk["couple_place_gratuit"]) >= 2:
            return f"🤝 **Meilleur duo conseillé** : N°{tk['couple_place_gratuit'][0]} - N°{tk['couple_place_gratuit'][1]}."
        if len(classement) >= 2:
            a, b = classement[0], classement[1]
            return f"🤝 **Meilleur duo (top 2 du classement)** : N°{a.get('numero')} {a.get('nom')} et N°{b.get('numero')} {b.get('nom')}."
        return "Aucun duo ne peut être calculé pour le moment."

    # --- Quarté ---
    if "quarté" in q or "quarte" in q:
        if tk["quarte_premium"]:
            return "🎯 **Quarté Premium conseillé** : " + " - ".join(tk["quarte_premium"])
        return "Aucun Quarté disponible pour le moment."

    # --- Trio ---
    if "trio" in q:
        if tk["trio_premium"]:
            return "🎯 **Trio Premium conseillé** : " + " - ".join(tk["trio_premium"])
        return "Aucun Trio disponible pour le moment."

    # --- Champ réduit ---
    if "champ réduit" in q or "champ reduit" in q:
        champ = tk["champ_reduit"]
        if champ.get("disponible") and champ.get("format"):
            return f"🔒 **Champ réduit Premium** : {champ['format']}"
        return "Le champ réduit n'est pas disponible pour cette course (trop peu de partants analysés)."

    # --- Dernière minute / joker ---
    if any(k in q for k in ["dernière minute", "derniere minute", "joker"]):
        derniere = tk["derniere_minute"]
        if derniere.get("selection"):
            texte = "⚡ **Ticket Dernière Minute** : " + " - ".join(derniere["selection"])
            if derniere.get("joker"):
                texte += f" (Joker : N°{derniere['joker']})"
            return texte
        return "Aucun ticket Dernière Minute disponible pour le moment."

    # --- Avis général sur la course ---
    if any(k in q for k in ["comment tu trouve", "comment tu vois", "avis sur cette course", "ton avis", "que penses-tu", "analyse de la course", "analyse moi", "analyse cette course"]):
        if not classement:
            return "Aucune analyse de course n'est disponible pour le moment."
        nb = len(classement)
        return (
            f"📊 Sur les {nb} partants : {_analyser_favori(classement)}\n\n"
            f"{_analyser_vulnerables(classement)}"
        )

    if any(k in q for k in ["favori", "coup sur", "meilleur", "gagnant", "top"]):
        return _analyser_favori(classement)

    if any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        if any(k in q for k in ["demain", "hier"]):
            return ("Le choix du Quinté d'un autre jour (hier/demain) n'est pas "
                    "encore disponible — cette fonctionnalité dépend d'une donnée "
                    "supplémentaire non encore branchée. Je peux en revanche vous "
                    "donner le Quinté du jour en cours.")
        if "premium" in q and tk["quinte_premium"]:
            return "💎 **Quinté Premium conseillé** : " + " - ".join(tk["quinte_premium"])
        if tk["quinte_gratuit"]:
            return "💡 **Ticket Quinté Conseillé** : " + " - ".join(tk["quinte_gratuit"])
        return "Aucune combinaison Quinté disponible pour le moment."

    if any(k in q for k in ["outsider", "tocard", "surprise", "pépite", "pepite"]):
        outsiders = [c for c in classement if float(c.get("cote", 0) or 0) >= 10.0]
        if outsiders:
            c = outsiders[0]
            return f"🔥 **Outsider à surveiller** : N°{c.get('numero')} **{c.get('nom')}** (Cote : {c.get('cote')})."
        return "Aucun outsider n'a été repéré avec un niveau de confiance suffisant."

    if "badge" in q or "signification" in q:
        return ("🏷️ **Guide des Badges** :\n- **D4** : Déferré des 4 pieds.\n"
                "- **Duo Chaud 🔥** : Jockey & entraîneur en réussite.\n"
                "- **Spécialiste 🎯** : aptitude détectée.\n"
                "- **Rachat ⚡** : profil à reconsidérer.")

    return ("Je n'ai pas identifié votre demande. Je peux : donner le favori, "
            "repérer les favoris vulnérables, comparer deux chevaux "
            "(ex. \"compare le 3 et le 7\"), proposer des scénarios, "
            "expliquer un cheval précis (fiche complète, jockey, musique, "
            "forme, corde...), donner le meilleur duo, le Quinté, Quarté, "
            "Trio, le champ réduit, le ticket Dernière Minute, les "
            "outsiders ou les badges AZ Turf Pro.")


def _enrichir_contexte_local(question: str, contexte: dict) -> tuple[dict, object]:
    """Construit un plan local et des résultats complémentaires.
    Aucun score AZ n'est modifié ; les résultats sont uniquement ajoutés au contexte.
    """
    contexte = dict(contexte or {})
    moteur = dict(contexte.get("moteur") or {})
    classement = list(moteur.get("classement") or [])
    plan = _planifier_demande(question, contexte) if _planifier_demande else None
    if plan:
        contexte["plan_chatbot"] = {
            "intentions": plan.intentions, "chevaux": plan.chevaux,
            "modules": plan.modules, "strategie": plan.strategie,
            "comparaison_az": plan.comparaison_az, "demande_detaillee": plan.demande_detaillee
        }
        if plan.chevaux:
            contexte["derniers_chevaux"] = plan.chevaux
        if classement:
            if "valeur" in plan.modules and _analyser_valeur:
                contexte["analyse_valeur"] = _analyser_valeur(classement)
            if "scenarios" in plan.modules and _resume_scenarios:
                contexte["resume_scenarios"] = _resume_scenarios(classement, contexte.get("course"))
            if "arbitre" in plan.modules and _resume_arbitre:
                contexte["arbitrage_az_ia"] = _resume_arbitre(classement)
    return contexte, plan


def _enrichir_contexte_modules_accompagnement(question: str, contexte: dict, historique: list | None = None) -> dict:
    """Branche en bloc les modules d'accompagnement historiques (orchestrateur_turf.py)
    sur le contexte déjà construit.

    Purement additif : seules les clés absentes du contexte existant sont
    ajoutées. La clé "plan_chatbot" n'est jamais reprise ici, car elle est
    déjà gérée par le plan d'orchestration existant (intent_orchestrator,
    utilisé par _enrichir_contexte_local et _reponse_plan_local) — on ne
    veut pas la remplacer par le plan (structure différente) d'orchestrateur_turf.
    Toute panne d'un module est silencieuse : le contexte d'origine est
    retourné inchangé.
    """
    if not _enrichir_accompagnement_bloc:
        return contexte
    try:
        enrichi = _enrichir_accompagnement_bloc(dict(contexte or {}), question, historique)
    except Exception:
        return contexte
    if not isinstance(enrichi, dict):
        return contexte
    for cle, valeur in enrichi.items():
        if cle == "plan_chatbot":
            continue
        if cle not in contexte:
            contexte[cle] = valeur
    return contexte


def _resume_modules_accompagnement(contexte: dict) -> str:
    """Formate, pour le system prompt, les résultats des modules d'accompagnement
    fraîchement branchés — uniquement ceux qui ont produit un résultat exploitable."""
    sections = []
    libelles = [
        ("tendances_cotes", "TENDANCES DE COTES"),
        ("consensus_presse", "CONSENSUS PRESSE"),
        ("impact_meteo", "MÉTÉO / TERRAIN"),
        ("expert_accompagnement", "EXPERT — RÉPONSE CIBLÉE"),
        ("expert_marche", "EXPERT — MARCHÉ"),
        ("expert_performance", "EXPERT — PERFORMANCE"),
        ("expert_conditions", "EXPERT — CONDITIONS"),
        ("expert_valeur", "EXPERT — VALEUR"),
        ("synthese_pronostiqueur", "SYNTHÈSE PRONOSTIQUEUR"),
        ("tactique", "TACTIQUE DE COURSE"),
        ("rythme_course", "RYTHME DE COURSE"),
        ("raisonnement_autonome", "RAISONNEMENT AUTONOME"),
        ("strategies", "STRATÉGIES DE TICKET"),
        ("connaissance_turf", "LEXIQUE TURF"),
        ("actualites", "ACTUALITÉS HIPPIQUES"),
    ]
    for cle, titre in libelles:
        valeur = contexte.get(cle)
        if not valeur:
            continue
        sections.append(f"=== {titre} (module d'accompagnement) ===\n{valeur}")
    return "\n\n".join(sections)


# =====================================
# POINT D'ENTRÉE
# =====================================

def repondre_assistant_turf(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    contexte = contexte_analyse or {}
    try:
        contexte, plan = _enrichir_contexte_local(question, contexte)
    except Exception:
        plan = None

    # Branchement en bloc des modules d'accompagnement (orchestrateur_turf.py) :
    # additif uniquement, voir _enrichir_contexte_modules_accompagnement.
    contexte = _enrichir_contexte_modules_accompagnement(question, contexte, historique)

    try:
        system_prompt = _construire_system_prompt(contexte)
        if plan:
            system_prompt += ("\n\n=== PLAN D'ORCHESTRATION LOCAL ===\n"
                              f"Intentions : {', '.join(plan.intentions)}\n"
                              f"Chevaux concernés : {', '.join(plan.chevaux) or 'aucun'}\n"
                              f"Modules à croiser : {', '.join(plan.modules)}\n"
                              "Ce plan sert de guide : ne l'invente pas comme un résultat et "
                              "n'utilise que les données réellement présentes.\n")
            if contexte.get("analyse_valeur"):
                system_prompt += "\n=== ANALYSE DE VALEUR ===\n" + _resume_valeur(contexte.get("moteur", {}).get("classement", []))
            if contexte.get("resume_scenarios"):
                system_prompt += "\n=== SCÉNARIOS ===\n" + contexte["resume_scenarios"]
            if contexte.get("arbitrage_az_ia"):
                system_prompt += "\n=== ARBITRAGE AZ / IA ===\n" + contexte["arbitrage_az_ia"]
        resume_accompagnement = _resume_modules_accompagnement(contexte)
        if resume_accompagnement:
            system_prompt += "\n\n" + resume_accompagnement
        messages = _historique_pour_ia(historique)

        ordre = [AI_PROVIDER] + [p for p in ("anthropic", "openai") if p != AI_PROVIDER]
        appels = {"anthropic": _appeler_claude, "openai": _appeler_openai}

        for fournisseur in ordre:
            appel = appels.get(fournisseur)
            if appel is None:
                continue
            try:
                texte = appel(system_prompt, messages, question)
                return {"status": "success", "question": question, "reponse": texte, "source": fournisseur}
            except Exception:
                continue
    except Exception:
        pass

    # Aucune IA disponible/configurée, ou donnée de course imprévue :
    # repli sans jamais laisser d'erreur brute remonter au client.
    source_secours = "secours"
    try:
        texte = _reponse_secours(question, contexte)
        non_identifiee = texte.startswith("Je n'ai pas identifié")
        if plan and not non_identifiee:
            # Les réponses historiques restent prioritaires ; les compléments
            # calculés localement sont ajoutés uniquement lorsqu'ils répondent à la demande.
            pass
        elif plan:
            modules = ", ".join(plan.modules)
            texte = (f"Je peux traiter cette demande à partir de la course courante. "
                     f"Je vais croiser : {modules}.\n\n" + texte)
        # Palier additif : uniquement lorsque le secours existant ne reconnaît
        # pas la demande (avant l'ajout éventuel du préfixe ci-dessus), on
        # tente orchestrateur_v20.py — il consomme le contexte déjà enrichi
        # par orchestrateur_turf.py (cotes, presse, météo, tactique,
        # raisonnement autonome...). S'il ne trouve rien de mieux, le message
        # de secours existant est conservé tel quel.
        if non_identifiee and _repondre_orchestrateur_v20:
            try:
                resultat_v20 = _repondre_orchestrateur_v20(question, contexte, historique)
            except Exception:
                resultat_v20 = None
            if isinstance(resultat_v20, dict) and resultat_v20.get("reponse"):
                texte = str(resultat_v20["reponse"])
                source_secours = "secours_orchestrateur_v20"
    except Exception:
        texte = ("Je rencontre une difficulté technique passagère. "
                 "Réessayez dans un instant.")
    return {"status": "success", "question": question, "reponse": texte, "source": source_secours}
