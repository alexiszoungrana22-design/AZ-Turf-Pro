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


def _reponse_secours(question: str, contexte: dict) -> str:
    import re as _re

    q = question.lower().strip()
    moteur = (contexte or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})
    course = (contexte or {}).get("course", {}) or {}

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

    # --- Meilleur duo / couplé ---
    if any(k in q for k in ["duo", "couple", "couplé", "gagnant placé", "gagnant/placé"]):
        couple = (tickets.get("gratuit") or {}).get("couple_gagnant_place") or (tickets.get("gratuit") or {}).get("couple_place")
        if couple:
            premiere = couple[0] if isinstance(couple, list) and couple else couple
            if isinstance(premiere, list):
                return f"🤝 **Meilleur duo conseillé** : N°{premiere[0]} - N°{premiere[1]}."
        if len(classement) >= 2:
            a, b = classement[0], classement[1]
            return f"🤝 **Meilleur duo (top 2 du classement)** : N°{a.get('numero')} {a.get('nom')} et N°{b.get('numero')} {b.get('nom')}."
        return "Aucun duo ne peut être calculé pour le moment."

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
        quinte = (tickets.get("gratuit") or {}).get("quinte", [])
        if quinte:
            nums = [str(c.get("numero")) for c in quinte]
            return "💡 **Ticket Quinté Conseillé** : " + " - ".join(nums)
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
            "expliquer un cheval précis, donner le meilleur duo, la "
            "sélection Quinté, les outsiders ou les badges AZ Turf Pro.")


# =====================================
# POINT D'ENTRÉE
# =====================================

def repondre_assistant_turf(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    contexte = contexte_analyse or {}

    try:
        system_prompt = _construire_system_prompt(contexte)
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
    try:
        texte = _reponse_secours(question, contexte)
    except Exception:
        texte = ("Je rencontre une difficulté technique passagère. "
                 "Réessayez dans un instant.")
    return {"status": "success", "question": question, "reponse": texte, "source": "secours"}
