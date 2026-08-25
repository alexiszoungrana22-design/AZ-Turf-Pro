"""AZ TURF PRO — Assistant conversationnel IA & Mémoire Avancée
Un pronostiqueur hippique et analyste, pas un chatbot à commandes :
la question est envoyée telle quelle à un modèle de langage (Claude ou
OpenAI), avec le contexte complet de la course et l'historique des archives,
pour un vrai raisonnement et une conversation naturelle sur n'importe quelle formulation.

Configuration (variables d'environnement, sur Render → Environment) :
  ANTHROPIC_API_KEY   clé Claude (prioritaire par défaut)
  OPENAI_API_KEY      clé OpenAI (utilisée en secours, ou en priorité si
                       AI_PROVIDER=openai)
  AI_PROVIDER         "anthropic" (défaut) ou "openai"

Si aucune des deux clés n'est configurée, ou si les deux appels échouent
(réseau, quota...), l'assistant retombe sur un moteur de secours intelligent
et élargi capable de fouiller dans les archives et d'analyser les performances.
[cite: 10]

import os
import json
import httpx
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").strip().lower()

CLAUDE_MODEL = "claude-sonnet-5"
OPENAI_MODEL = "gpt-4o-mini"

TIMEOUT_SECONDES = 25

# =====================================
# MÉMOIRE PERSISTANTE DES COURSES PASSÉES
# =====================================
MEMOIRE_COURSES_ARCHIVES = {}

def archiver_course_passee(id_course: str, contexte_course: dict, arrivee_officielle: list) -> dict:
    """Enregistre une course terminée dans la mémoire à long terme de l'assistant."""
    if not id_course:
        id_course = f"COURSE_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    MEMOIRE_COURSES_ARCHIVES[id_course] = {
        "id_course": id_course,
        "date_archivage": datetime.now().isoformat(),
        "contexte": contexte_course,
        "arrivee_officielle": [str(x) for x in arrivee_officielle]
    }
    return {
        "status": "success",
        "message": f"Course {id_course} archivée avec succès dans la mémoire.",
        "total_archives": len(MEMOIRE_COURSES_ARCHIVES)
    }

def rechercher_memoire_historique(requete: str) -> str:
    """Permet à l'assistant de fouiller dans les courses passées."""
    if not MEMOIRE_COURSES_ARCHIVES:
        return "Aucune course passée n'est actuellement enregistrée dans ma mémoire d'archives."

    requete = requete.lower()
    matches = []

    for cid, data in MEMOIRE_COURSES_ARCHIVES.items():
        course_info = data.get("contexte", {}).get("course", {})
        hippodrome = str(course_info.get("hippodrome", "")).lower()
        date_c = str(course_info.get("date", "")).lower()
        
        if requete in cid.lower() or requete in hippodrome or requete in date_c or requete in "toutes":
            matches.append(data)

    if not matches:
        return f"Je n'ai trouvé aucune archive correspondant à '{requete}' dans mes mémoires."

    reponses = []
    for m in matches[-3:]:
        c_info = m["contexte"].get("course", {})
        arrivee = ", ".join(m["arrivee_officielle"])
        reponses.append(
            f"• **{c_info.get('hippodrome', 'Hippodrome inconnu')}** du {c_info.get('date', 'date inconnue')} "
            f"(R{c_info.get('reunion', '?')}C{c_info.get('course_numero', '?')}) — "
            f"**Arrivée officielle** : [ {arrivee} ]"
        )

    return "🧠 **Archives & Souvenirs de courses** :\n" + "\n".join(reponses)


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
        ligne += f" | musique : {cheval.get('musique_brute', '-')}"
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
    # Intégration de la mémoire des courses passées dans le prompt de l'IA
    memoire_recente = ""
    if MEMOIRE_COURSES_ARCHIVES:
        memoire_recente = "\n=== COURSES PASSÉES EN MÉMOIRE ===\n"
        for cid, data in list(MEMOIRE_COURSES_ARCHIVES.items())[-3:]:
            c_inf = data.get("contexte", {}).get("course", {})
            memoire_recente += f"- {c_inf.get('hippodrome', 'Piste')} ({c_inf.get('date', '-')}) | Arrivée : {', '.join(data.get('arrivee_officielle', []))}\n"

    return (
        "Tu es AZ Turf Pro, un pronostiqueur hippique professionnel, "
        "reconnu et confiant, qui échange avec les abonnés d'une "
        "application de pronostics Quinté+. Tu possèdes une mémoire avancée "
        "des courses actuelles et passées.\n\n"
        "Règles :\n"
        "- Réponds en français, avec l'assurance d'un vrai professionnel "
        "du turf qui connaît sa course sur le bout des doigts.\n"
        "- Appuie-toi sur les données de course et sur les archives passées si l'utilisateur y fait référence.\n"
        "- Utilise activement toutes les statistiques à ta disposition (cotes, smart money, indices AZ, musique, driver, ferrage).\n\n"
        f"{memoire_recente}\n"
        "=== DONNÉES DE LA COURSE ACTUELLE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO ===\n"
        f"{_resume_classement(contexte)}\n\n"
        "=== TICKETS GÉNÉRÉS ===\n"
        f"{_resume_tickets(contexte)}\n"
    )


def _historique_pour_ia(historique: list, limite: int = 12) -> list:
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
# APPELS AUX MODÈLES (CLAUDE / OPENAI)
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
# MOTEUR D'ANALYSE LOCAL & MÉMOIRE
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
    return f"🎯 **Favori AZ Turf Pro** : N°{top.get('numero')} **{top.get('nom')}** (Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')})."


def _reponse_secours(question: str, contexte: dict) -> str:
    import re as _re

    q = question.lower().strip()
    moteur = (contexte or {}).get("moteur", {})
    classement = moteur.get("classement", [])

    # --- Gestion de la mémoire et des courses passées ---
    if any(k in q for k in ["rappelle", "souviens", "historique", "precedente", "précédente", "archives", "course passée"]):
        return rechercher_memoire_historique(q)

    # --- Salutations ---
    if any(k in q for k in ["bonjour", "salut", "bonsoir", "hello", "coucou"]):
        return ("👋 Bonjour ! Je suis AZ Turf Pro. J'ai en mémoire nos analyses de courses "
                "et je peux décortiquer les partants du jour, comparer les cotes ou fouiller dans nos archives. Que souhaitez-vous faire ?")

    numeros_cites = _re.findall(r"\b(\d{1,2})\b", q)
    
    # --- Analyse d'un cheval précis ---
    if numeros_cites and any(k in q for k in ["jockey", "driver", "entraineur", "musique", "forme", "gains", "corde", "ferrage"]):
        cheval = _trouver_cheval(classement, numeros_cites[0])
        if cheval:
            return f"📋 **Fiche N°{cheval.get('numero')} {cheval.get('nom')}** — Driver : {cheval.get('driver', '-')} | Cote : {cheval.get('cote', '-')} | Indice AZ : {cheval.get('indice_az', '-')}"

    if any(k in q for k in ["favori", "coup sur", "base"]):
        return _analyser_favori(classement)

    return ("🧠 Je suis configuré pour analyser vos courses en direct et me souvenir des sessions passées. "
            "Posez-moi une question sur un partant, un comparatif ou demandez-moi de fouiller dans nos archives !")


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

    try:
        texte = _reponse_secours(question, contexte)
    except Exception:
        texte = "Je rencontre une difficulté technique passagère. Réessayez dans un instant."
    return {"status": "success", "question": question, "reponse": texte, "source": "secours"}
