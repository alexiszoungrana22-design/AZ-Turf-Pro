"""
AZ TURF PRO - MODULE MÉMOIRE & HISTORIQUE AVANCÉ DU CHATBOT
Fichier : backend/modules/chatbot_memory.py

Corrigé : la version précédente archivait dans un dict Python en
mémoire (MEMOIRE_COURSES_ARCHIVES) que personne n'alimentait jamais et
qui de toute façon se vidait à chaque redémarrage du serveur (process
Render éphémère). Cette version s'appuie directement sur le vrai
historique persistant écrit par learning.py (backend/data/historique_az.json),
qui est la seule source réellement alimentée par l'application
(engine.lancer_analyse -> enregistrer_course à chaque analyse).
"""

from datetime import datetime


def _historique_reel():
    try:
        from learning import lire_historique
        return lire_historique() or []
    except Exception:
        return []


def rechercher_memoire_historique(requete: str) -> str:
    """
    Recherche dans les vraies courses déjà analysées par l'application
    (hippodrome, date, réunion/numéro de course).
    """
    historique = _historique_reel()
    if not historique:
        return "Aucune course passée n'est actuellement enregistrée dans mon historique."

    requete = (requete or "").strip().lower()
    if not requete:
        return "Précise l'hippodrome, la date ou la course que tu cherches."

    matches = []
    for course in historique:
        if not isinstance(course, dict):
            continue
        info = course.get("course") or {}
        hippodrome = str(info.get("hippodrome", course.get("hippodrome", ""))).lower()
        date_c = str(info.get("date", course.get("date", ""))).lower()
        reunion = str(info.get("reunion", course.get("reunion", ""))).lower()
        if requete in hippodrome or requete in date_c or requete in reunion:
            matches.append(course)

    if not matches:
        return f"Je n'ai trouvé aucune course correspondant à « {requete} » dans mon historique."

    reponses = []
    for m in matches[-3:]:
        info = m.get("course") or {}
        arrivee = m.get("arrivee") or m.get("arrivee_officielle") or []
        arrivee_txt = ", ".join(str(a) for a in arrivee) if arrivee else "pas encore connue"
        reponses.append(
            f"• **{info.get('hippodrome', 'Hippodrome inconnu')}** du {info.get('date', 'date inconnue')} "
            f"(R{info.get('reunion', '?')}C{info.get('course_numero', '?')}) — "
            f"Arrivée officielle : [ {arrivee_txt} ]"
        )

    return "🧠 **Courses retrouvées dans l'historique**\n" + "\n".join(reponses)


def generer_contexte_memoire_recent(limite: int = 5) -> str:
    """
    Résumé textuel des dernières courses réellement analysées, pour
    contexte interne (jamais présenté comme des données inventées).
    """
    historique = _historique_reel()
    if not historique:
        return "Aucun historique de course passée en mémoire."

    lignes = ["=== DERNIÈRES COURSES ANALYSÉES ==="]
    for course in historique[-limite:]:
        if not isinstance(course, dict):
            continue
        info = course.get("course") or {}
        arrivee = course.get("arrivee") or course.get("arrivee_officielle") or []
        lignes.append(
            f"- {info.get('hippodrome', course.get('hippodrome', '-'))} "
            f"({info.get('date', course.get('date', '-'))}) "
            f"| Arrivée : {', '.join(str(a) for a in arrivee) if arrivee else 'inconnue'}"
        )
    return "\n".join(lignes)


def nombre_courses_archivees() -> int:
    return len(_historique_reel())
