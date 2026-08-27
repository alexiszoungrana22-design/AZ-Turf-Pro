"""
AZ TURF PRO - MODULE MÉMOIRE & HISTORIQUE AVANCÉ DU CHATBOT
Fichier : backend/modules/chatbot_memory.py
"""

import json
from datetime import datetime

# Mémoire globale persistante ou tampon pour la session/serveur
MEMOIRE_COURSES_ARCHIVES = {}

def archiver_course_passee(id_course: str, contexte_course: dict, arrivee_officielle: list) -> dict:
    """
    Enregistre une course terminée dans la mémoire à long terme de l'assistant,
    en combinant les données de course, le classement AZ et l'arrivée officielle.
    """
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
        "message": f"Course {id_course} archivée avec succès dans la mémoire de l'assistant.",
        "total_archives": len(MEMOIRE_COURSES_ARCHIVES)
    }


def rechercher_memoire_historique(requete: str) -> str:
    """
    Permet à l'assistant de fouiller dans les courses passées en fonction
    d'un mot-clé (nom d'hippodrome, date, numéro de course).
    """
    if not MEMOIRE_COURSES_ARCHIVES:
        return "Aucune course passée n'est actuellement enregistrée dans ma mémoire d'archives."

    requete = requete.lower()
    matches = []

    for cid, data in MEMOIRE_COURSES_ARCHIVES.items():
        course_info = data.get("contexte", {}).get("course", {})
        hippodrome = str(course_info.get("hippodrome", "")).lower()
        date_c = str(course_info.get("date", "")).lower()
        
        if requete in cid.lower() or requete in hippodrome or requete in date_c:
            matches.append(data)

    if not matches:
        return f"Je n'ai trouvé aucune archive correspondant à '{requete}' dans mes mémoires."

    # Formater le résumé des courses trouvées
    reponses = []
    for m in matches[-3:]:  # Limiter aux 3 derniers résultats pertinents
        c_info = m["contexte"].get("course", {})
        arrivee = ", ".join(m["arrivee_officielle"])
        reponses.append(
            f"• **{c_info.get('hippodrome', 'Hippodrome inconnu')}** du {c_info.get('date', 'date inconnue')} "
            f"(R{c_info.get('reunion', '?')}C{c_info.get('course_numero', '?')}) — "
            f"**Arrivée officielle** : [ {arrivee} ]"
        )

    return "🧠 **Archives retrouvées** :\n" + "\n".join(reponses)


def generer_contexte_memoire_recent() -> str:
    """
    Génère un résumé textuel des dernières courses en mémoire pour l'injecter
    dans le prompt système de l'IA (Claude/OpenAI) ou du moteur de secours.
    """
    if not MEMOIRE_COURSES_ARCHIVES:
        return "Aucun historique de course passée en mémoire."
    
    lignes = ["=== MÉMOIRE DES COURSES PRÉCÉDENTES ==="]
    for cid, data in list(MEMOIRE_COURSES_ARCHIVES.items())[-5:]:
        c_inf = data.get("contexte", {}).get("course", {})
        lignes.append(
            f"- Course {cid} à {c_inf.get('hippodrome', '-')} ({c_inf.get('date', '-')}) "
            f"| Arrivée : {', '.join(data.get('arrivee_officielle', []))}"
        )
    return "\n".join(lignes)
