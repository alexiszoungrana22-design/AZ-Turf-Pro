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

# MODE AUTONOME AZ TURF PRO
# Claude/OpenAI sont volontairement désactivés pour cette version.
# Le chatbot repose uniquement sur le moteur AZ, les données PMU/France Galop
# déjà disponibles et l'historique local du projet.
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

    return (
        f"🎯 **Favori AZ Turf Pro** : N°{top.get('numero')} **{top.get('nom')}** "
        f"(Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')}). {confiance}"
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
        f"- Jockey/Driver : {driver}\n"
        f"- Entraîneur : {cheval.get('entraineur', '-')}\n"
        f"- Cote : {cheval.get('cote', '-')} (tendance {tendance}) | Indice AZ : {cheval.get('indice_az', '-')} | "
        f"Indice Premium : {cheval.get('indice_premium', '-')}\n"
        f"- Musique (forme récente) : {cheval.get('musique_brute', '-')}"
    )
    if forme is not None:
        fiche += f" — forme {forme}/10"
        if regularite is not None:
            fiche += f", régularité {regularite}/10"
    fiche += (
        f"\n- Gains de carrière : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}\n"
        f"- Corde : {cheval.get('corde', '-')} | Ferrage : {cheval.get('deferre', '-')}"
    )
    return fiche


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
                f"cote actuelle {cheval.get('cote', '-')} (tendance {
