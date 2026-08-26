"""AZ TURF PRO â€” Assistant conversationnel IA
Un pronostiqueur hippique et analyste, pas un chatbot Ã  commandes :
la question est envoyÃ©e telle quelle Ã  un modÃ¨le de langage (Claude ou
OpenAI), avec le contexte complet de la course, pour un vrai raisonnement
et une conversation naturelle sur n'importe quelle formulation.

Configuration (variables d'environnement, sur Render â†’ Environment) :
  ANTHROPIC_API_KEY   clÃ© Claude (prioritaire par dÃ©faut)
  OPENAI_API_KEY      clÃ© OpenAI (utilisÃ©e en secours, ou en prioritÃ© si
                       AI_PROVIDER=openai)
  AI_PROVIDER         "anthropic" (dÃ©faut) ou "openai"

Si aucune des deux clÃ©s n'est configurÃ©e, ou si les deux appels Ã©chouent
(rÃ©seau, quota...), l'assistant retombe sur une rÃ©ponse minimale par
mots-clÃ©s pour ne jamais laisser le client sans rÃ©ponse.
"""

import os
import json
import httpx

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
        f"RÃ©union/Course : {course.get('reunion', '-')} / "
        f"{course.get('course_numero', '-')} â€” {course.get('course', '-')}",
        f"Hippodrome : {course.get('hippodrome', '-')}",
        f"Discipline : {course.get('discipline', '-')} sur "
        f"{course.get('distance_course', '-')} m",
        f"Date / heure de dÃ©part : {course.get('date', '-')} "
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
            f"NÂ°{cheval.get('numero', '?')} {cheval.get('nom', '?')} "
            f"({cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}) â€” "
            f"jockey/driver : {driver}, "
            f"entraÃ®neur : {cheval.get('entraineur', '-')} | "
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
                ligne += f", rÃ©gularitÃ© {regularite}/10"
            ligne += ")"
        ligne += (
            f", gains carriÃ¨re : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}, "
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
        "reconnu et confiant, qui Ã©change avec les abonnÃ©s d'une "
        "application de pronostics QuintÃ©+. Tu n'es pas un menu de "
        "commandes : tu comprends et rÃ©ponds naturellement Ã  n'importe "
        "quelle question, mÃªme formulÃ©e diffÃ©remment de ce qui est prÃ©vu, "
        "et tu maÃ®trises toutes les statistiques disponibles (cotes, "
        "tendances de cote, indices AZ et Premium, driver/jockey, "
        "entraÃ®neur, musique, forme, rÃ©gularitÃ©, corde, ferrage, gains "
        "carriÃ¨re).\n\n"
        "RÃ¨gles :\n"        "- Comprends l'intention avant de rÃ©pondre : une question jamais prÃ©vue doit quand mÃªme recevoir une rÃ©ponse argumentÃ©e.\n"
        "- Utilise l'historique pour comprendre Â« le 7 Â», Â« celui d'avant Â», Â« retire le 4 Â» ou Â« notre ticket Â».\n"
        "- Les exemples connus ne constituent pas une liste fermÃ©e de commandes.\n"
        "- Pour toute question hippique libre, raisonne Ã  partir des donnÃ©es rÃ©ellement disponibles.\n"

        "- RÃ©ponds en franÃ§ais, avec l'assurance d'un vrai professionnel "
        "du turf qui connaÃ®t sa course sur le bout des doigts â€” direct, "
        "net, sans formules d'hÃ©sitation inutiles (\"je pense que\", "
        "\"peut-Ãªtre\" Ã  Ã©viter sauf incertitude rÃ©elle sur la donnÃ©e).\n"
        "- Appuie-toi uniquement sur les donnÃ©es de course fournies "
        "ci-dessous. N'invente jamais de cote, de nom de cheval, de "
        "jockey ou de rÃ©sultat qui n'y figure pas.\n"
        "- Si une information prÃ©cise demandÃ©e n'est pas dans les "
        "donnÃ©es (ex. un historique dÃ©taillÃ© non fourni), dis-le "
        "honnÃªtement plutÃ´t que de l'inventer â€” mais formule Ã§a comme "
        "une limite ponctuelle, pas comme une excuse gÃ©nÃ©rale.\n"
        "- Utilise activement TOUTES les statistiques Ã  ta disposition : "
        "la musique et la forme rÃ©cente, le driver, l'entraÃ®neur, la "
        "corde, le ferrage, les tendances de cote (argent qui rentre ou "
        "sort) sont autant d'arguments Ã  mobiliser, pas seulement "
        "l'indice AZ brut.\n"
        "- Argumente, compare, nuance, donne un vrai avis tranchÃ© "
        "d'analyste â€” pas seulement rÃ©citer des chiffres.\n"
        "- Reste concis (quelques phrases ou un court paragraphe), sauf "
        "si la question demande explicitement plus de dÃ©tail.\n\n"
        "=== DONNÃ‰ES DE LA COURSE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO (toutes statistiques disponibles) ===\n"
        f"{_resume_classement(contexte)}\n\n"
        "=== TICKETS GÃ‰NÃ‰RÃ‰S ===\n"
        f"{_resume_tickets(contexte)}\n"
        "=== HISTORIQUE DE CONVERSATION ===\n"
        f"{json.dumps(_historique_pour_ia(contexte.get('historique') or []), ensure_ascii=False, default=str)}\n"
    )


def _historique_pour_ia(historique: list, limite: int = 12) -> list:
    """Normalise l'historique envoyÃ© par le frontend (chatbot.js) vers un
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
# APPELS AUX MODÃˆLES
# =====================================

def _appeler_claude(system_prompt: str, messages: list, question: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY non configurÃ©e.")

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
        raise RuntimeError("RÃ©ponse Claude vide.")
    return texte


def _appeler_openai(system_prompt: str, messages: list, question: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY non configurÃ©e.")

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
        raise RuntimeError("RÃ©ponse OpenAI vide.")
    return texte


# =====================================
# REPLI SANS IA (aucune clÃ© configurÃ©e / Ã©chec des deux appels)
# =====================================

# =====================================
# MOTEUR D'ANALYSE RÃ‰EL (raisonnement sur les donnÃ©es, sans IA externe)
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
        confiance = "Il se dÃ©tache nettement du reste du peloton â€” un favori solide."
    elif ecart is not None and ecart >= 1.5:
        confiance = "Il devance ses poursuivants avec une marge correcte, mais sans Ãªtre hors de portÃ©e."
    elif ecart is not None:
        confiance = f"L'Ã©cart avec le NÂ°{classement[1].get('numero')} n'est que de {ecart} points â€” course ouverte, ce favori peut Ãªtre renversÃ©."
    else:
        confiance = "Seul cheval rÃ©ellement analysÃ© sur cette course."

    return (
        f"ðŸŽ¯ **Favori AZ Turf Pro** : NÂ°{top.get('numero')} **{top.get('nom')}** "
        f"(Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')}). {confiance}"
    )


def _analyser_vulnerables(classement: list) -> str:
    if len(classement) < 2:
        return "Pas assez de chevaux analysÃ©s pour juger d'une vulnÃ©rabilitÃ©."

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
                raisons.append(f"talonnÃ© de prÃ¨s par le NÂ°{suivant.get('numero')} (Ã©cart de {round(ecart, 2)} pts)")
            if cote_elevee:
                raisons.append(f"une cote qui reste Ã©levÃ©e ({cheval.get('cote')})")
            vulnerables.append(f"- NÂ°{cheval.get('numero')} **{cheval.get('nom')}** : {', '.join(raisons)}.")

    if not vulnerables:
        return "Aucun favori ne semble particuliÃ¨rement vulnÃ©rable sur cette course â€” le classement paraÃ®t net."
    return "âš ï¸ **Favoris Ã  surveiller** :\n" + "\n".join(vulnerables)


def _comparer_chevaux(classement: list, num_a: str, num_b: str) -> str:
    a = _trouver_cheval(classement, num_a)
    b = _trouver_cheval(classement, num_b)
    if not a or not b:
        manquant = num_a if not a else num_b
        return f"Je ne trouve pas le numÃ©ro {manquant} dans le classement de cette course."

    rang_a = classement.index(a) + 1
    rang_b = classement.index(b) + 1
    diff = round(_indice(a) - _indice(b), 2)

    if diff > 0:
        verdict = f"NÂ°{num_a} **{a.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_a} vs {rang_b})."
    elif diff < 0:
        verdict = f"NÂ°{num_b} **{b.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_b} vs {rang_a})."
    else:
        verdict = "Les deux chevaux sont Ã  Ã©galitÃ© d'indice â€” un vrai coin de table."

    return (
        f"**NÂ°{num_a} {a.get('nom')}** (indice {a.get('indice_az', '-')}, cote {a.get('cote', '-')}) "
        f"vs **NÂ°{num_b} {b.get('nom')}** (indice {b.get('indice_az', '-')}, cote {b.get('cote', '-')}) : {verdict}"
    )


def _generer_scenarios(classement: list) -> str:
    if len(classement) < 3:
        return "Pas assez de chevaux analysÃ©s pour construire des scÃ©narios."

    favori, second, troisieme = classement[0], classement[1], classement[2]
    outsiders = [c for c in classement if _cote(c) >= 10]
    outsider = outsiders[0] if outsiders else classement[-1]

    return (
        "ðŸ›¤ï¸ **Deux scÃ©narios possibles** :\n\n"
        f"**ScÃ©nario logique** : le favori NÂ°{favori.get('numero')} **{favori.get('nom')}** confirme sa "
        f"place, devant NÂ°{second.get('numero')} **{second.get('nom')}** et NÂ°{troisieme.get('numero')} "
        f"**{troisieme.get('nom')}** â€” un ordre proche du classement AZ Turf Pro.\n\n"
        f"**ScÃ©nario surprise** : NÂ°{outsider.get('numero')} **{outsider.get('nom')}** "
        f"(cote {outsider.get('cote', '-')}) crÃ©e la sensation et vient bousculer le favori, "
        "profitant d'un faux rythme ou d'une mÃ©forme du leader."
    )


def _fiche_cheval(cheval: dict) -> str:
    driver = cheval.get("driver") or cheval.get("conducteur") or cheval.get("pilote") or cheval.get("jockey") or "-"
    forme = cheval.get("forme")
    regularite = cheval.get("regularite")
    tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"

    fiche = (
        f"**NÂ°{cheval.get('numero')} {cheval.get('nom')}** â€” "
        f"{cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}\n"
        f"- Jockey/Driver : {driver}\n"
        f"- EntraÃ®neur : {cheval.get('entraineur', '-')}\n"
        f"- Cote : {cheval.get('cote', '-')} (tendance {tendance}) | Indice AZ : {cheval.get('indice_az', '-')} | "
        f"Indice Premium : {cheval.get('indice_premium', '-')}\n"
        f"- Musique (forme rÃ©cente) : {cheval.get('musique_brute', '-')}"
    )
    if forme is not None:
        fiche += f" â€” forme {forme}/10"
        if regularite is not None:
            fiche += f", rÃ©gularitÃ© {regularite}/10"
    fiche += (
        f"\n- Gains de carriÃ¨re : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}\n"
        f"- Corde : {cheval.get('corde', '-')} | Ferrage : {cheval.get('deferre', '-')}"
    )
    return fiche


# =====================================
# RECHERCHE INDÃ‰PENDANTE EN DIRECT (PMU.fr)
# =====================================
#
# Contrairement au contexte habituel (calculÃ© une fois par le moteur
# AZ au dÃ©but de la conversation), cette fonction relance un VRAI
# appel rÃ©seau vers PMU.fr au moment prÃ©cis de la question, pour les
# demandes qui portent explicitement sur l'Ã©volution en direct
# (cotes, derniÃ¨re minute). Best-effort : Ã©chec toujours silencieux,
# ne casse jamais la conversation si PMU.fr est indisponible.

# =====================================
# ANALYSE RÃ‰TROSPECTIVE (courses passÃ©es + arrivÃ©es rÃ©elles)
# =====================================
#
# S'appuie sur learning.py / historique_az.json, dÃ©jÃ  alimentÃ©
# automatiquement par engine.py Ã  chaque /api/analyse. Permet de
# vraiment expliquer si la sÃ©lection AZ a fonctionnÃ© ou non, en
# comparant la sÃ©lection au classement d'arrivÃ©e officiel PMU.
#
# âš ï¸ LIMITE CONNUE (dÃ©jÃ  documentÃ©e dans api.py) : si l'hÃ©bergement
# Render ne dispose pas d'un disque persistant, ce fichier peut Ãªtre
# remis Ã  zÃ©ro Ã  chaque redÃ©ploiement â€” l'historique ne survivrait
# alors pas dans le temps. Ã€ vÃ©rifier concrÃ¨tement sur ton plan
# Render si cette fonctionnalitÃ© te semble incomplÃ¨te en usage rÃ©el.

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
            f"ðŸ“‹ **DerniÃ¨re course analysÃ©e** : {course.get('hippodrome', '-')} "
            f"({course.get('date', '-')}, {course.get('reunion', '-')}/{course.get('course_numero', '-')})",
            f"Notre sÃ©lection : {' - '.join(str(n) for n in selection_az[:7])}",
            f"ArrivÃ©e rÃ©elle : {' - '.join(str(n) for n in arrivee[:7])}" if arrivee else "ArrivÃ©e rÃ©elle : non disponible pour le moment.",
        ]

        if gagnant_reel and numero_favori:
            if gagnant_reel == numero_favori:
                lignes.append(
                    f"âœ… Notre favori (NÂ°{numero_favori}) a remportÃ© la course â€” "
                    "sÃ©lection gagnante confirmÃ©e."
                )
            elif gagnant_reel in [str(n) for n in selection_az[:7]]:
                rang = [str(n) for n in selection_az[:7]].index(gagnant_reel) + 1
                lignes.append(
                    f"âš ï¸ Le vrai gagnant (NÂ°{gagnant_reel}) figurait dans notre sÃ©lection "
                    f"(en position {rang}), mais pas en tÃªte â€” le favori NÂ°{numero_favori} "
                    "n'a pas confirmÃ© sa cote de sortie."
                )
            else:
                lignes.append(
                    f"âŒ Le gagnant rÃ©el (NÂ°{gagnant_reel}) ne figurait pas dans notre "
                    f"sÃ©lection â€” notre favori NÂ°{numero_favori} n'Ã©tait pas le bon choix "
                    "sur cette course, un imprÃ©vu (forme du jour, tactique de course, "
                    "terrain) a rebattu les cartes."
                )

        return "\n".join(lignes)
    except Exception:
        return None


def _rafraichir_cotes_pmu_direct(course_reference: di
