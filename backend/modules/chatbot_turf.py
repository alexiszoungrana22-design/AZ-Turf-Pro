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
    return "\n".join(lignes)


def _resume_classement(contexte: dict, limite: int = 20) -> str:
    moteur = (contexte or {}).get("moteur", {}) or {}
    classement = moteur.get("classement", []) or []
    lignes = []
    for cheval in classement[:limite]:
        if not isinstance(cheval, dict):
            continue
        lignes.append(
            f"N°{cheval.get('numero', '?')} {cheval.get('nom', '?')} — "
            f"cote {cheval.get('cote', '-')}, "
            f"indice AZ {cheval.get('indice_az', '-')}, "
            f"indice Premium {cheval.get('indice_premium', '-')}"
        )
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
        "Tu es AZ Turf Pro, un pronostiqueur hippique et analyste "
        "professionnel qui échange avec les abonnés d'une application "
        "de pronostics Quinté+. Tu n'es pas un menu de commandes : tu "
        "comprends et réponds naturellement à n'importe quelle question, "
        "même formulée différemment de ce qui est prévu.\n\n"
        "Règles :\n"
        "- Réponds en français, de façon claire et directe, comme un "
        "vrai analyste turfiste s'adressant à un joueur.\n"
        "- Appuie-toi uniquement sur les données de course fournies "
        "ci-dessous. N'invente jamais de cote, de nom de cheval ou de "
        "résultat qui n'y figure pas.\n"
        "- Si une information demandée n'est pas dans les données, "
        "dis-le honnêtement plutôt que de l'inventer.\n"
        "- Tu peux argumenter, comparer des chevaux, nuancer, donner ton "
        "avis d'analyste — pas seulement réciter des chiffres.\n"
        "- Reste concis (quelques phrases ou un court paragraphe), sauf "
        "si la question demande explicitement plus de détail.\n\n"
        "=== DONNÉES DE LA COURSE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO ===\n"
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
    reponse.raise_for_status()
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
    reponse.raise_for_status()
    data = reponse.json()
    texte = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    if not texte:
        raise RuntimeError("Réponse OpenAI vide.")
    return texte


# =====================================
# REPLI SANS IA (aucune clé configurée / échec des deux appels)
# =====================================

def _reponse_secours(question: str, contexte: dict) -> str:
    q = question.lower().strip()
    moteur = (contexte or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})

    if any(k in q for k in ["favori", "coup sur", "meilleur", "gagnant", "top"]):
        if classement:
            top = classement[0]
            return (
                f"🎯 **Le Coup Sûr AZ Turf Pro** est le N°{top.get('numero')} "
                f"**{top.get('nom')}** avec un Indice AZ de **{top.get('indice_az')}** "
                f"et un Indice Premium de **{top.get('indice_premium')}**."
            )
        return "Veuillez d'abord lancer une analyse de course pour identifier le favori."

    if any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
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

    return ("Je fonctionne actuellement en mode simplifié (aucune IA "
            "connectée pour l'instant). Posez-moi une question sur le "
            "favori, la sélection Quinté, les outsiders ou les badges "
            "AZ Turf Pro !")


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
