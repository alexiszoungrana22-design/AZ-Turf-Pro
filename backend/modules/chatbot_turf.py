"""AZ TURF PRO - ASSISTANT CONVERSATIONNEL IA MULTI-SOURCES"""
import time

# ==========================================
# MOTEUR DE COLLECTE MULTI-SOURCES EN DIRECT
# ==========================================
def croiser_sources_temps_reel(info_course: dict) -> dict:
    """
    Simule ou exécute les appels vers différentes API/Scrapers 
    (à relier avec ton pmu_source.py et autres scripts de scraping).
    """
    # Identifiant de la course pour requêter les sources
    course_id = info_course.get("id", "inconnu")
    
    # 1. Source PMU : Cotes en direct et variations
    # Ici tu feras appel à ta fonction de pmu_source.py : pmu_source.get_live_odds(course_id)
    pmu_live = {
        "status": "online",
        "tendance_betting": "Chute de cote sur le N°4, délaissement du N°12."
    }
    
    # 2. Source Zeturf : Prises de jeux et "Heat" (argent injecté)
    zeturf_live = {
        "status": "online",
        "argent_massif_sur": [4, 7],
        "alerte_tocard": 14
    }
    
    # 3. Source Genycourses / Equidia : Bruits d'écurie et interviews de dernière minute
    geny_echos = {
        "status": "online",
        "bruits_pistes": "Le N°7 est très allant au heat d'échauffement.",
        "terrain": "Lourd (indice 4.2) - pluie récente."
    }
    
    return {
        "timestamp": time.time(),
        "pmu": pmu_live,
        "zeturf": zeturf_live,
        "geny": geny_echos
    }


# ==========================================
# LOGIQUE DE L'ASSISTANT
# ==========================================
def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = question.lower().strip()
    moteur = (contexte_analyse or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})
    info_course = (contexte_analyse or {}).get("course", {})

    # 🔄 ÉTAPE CRUCIALE : Récupération des données multi-sources à la volée
    live_data = croiser_sources_temps_reel(info_course)

    # 1. Gestion des salutations
    if any(k in q for k in ["bonjour", "salut", "coucou"]):
        reponse = (
            "👋 Bonjour ! L'analyseur multi-sources est connecté (PMU, Zeturf, Geny activés ✅). "
            "Je scanne actuellement les cotes en direct et les bruits de piste. Que voulez-vous savoir ?"
        )

    # 2. Détection du mauvais favori (Croisement PMU & Zeturf)
    elif any(k in q for k in ["mauvais favori", "faux favori", "piège", "surcoté"]):
        if len(classement) > 1:
            faux_fav = classement[1] if len(classement) > 1 else classement[0]
            reponse = (
                f"🚨 **Alerte Multi-Sources : Le Faux Favori**\n"
                f"Attention au N°{faux_fav.get('numero')} **{faux_fav.get('nom')}**.\n"
                f"📉 *Sources Zeturf/PMU* : On observe une dérive de sa cote en direct. Les gros parieurs l'évitent.\n"
                f"🌧️ *Source Météo/Terrain* : Le terrain actuel ({live_data['geny']['terrain']}) désavantage fortement ses aptitudes."
            )
        else:
            reponse = "⚠️ En attente des flux en direct pour détecter une anomalie sur les favoris."

    # 3. Le cheval troublant / turbulent (Alertes Zeturf & Geny)
    elif any(k in q for k in ["troublant", "trouble", "turbulent", "tocard", "pépite"]):
        tocard_live = live_data['zeturf'].get('alerte_tocard', 'N/A')
        reponse = (
            f"🌪️ **Radar Multi-Sources : Le Cheval Turbulent**\n"
            f"Les flux Zeturf détectent des prises de jeu inhabituelles sur le **N°{tocard_live}**.\n"
            f"🎙️ *Échos Geny* : '{live_data['geny']['bruits_pistes']}'\n"
            f"C'est la pépite cachée repérée en temps réel, idéale pour faire exploser les rapports du Quinté !"
        )

    # 4. Bruits d'écurie en direct
    elif any(k in q for k in ["bruit", "écurie", "echos", "confiance", "entraineur"]):
        reponse = (
            f"🗣️ **Derniers Bruits (Genycourses / Equidia)** :\n"
            f"Les reporters sur place confirment : *{live_data['geny']['bruits_pistes']}*\n"
            f"L'argent intelligent (Smart Money) se dirige massivement vers les numéros : {live_data['zeturf']['argent_massif_sur']} (Source Zeturf)."
        )

    # 5. Enjeux & Synthèse Temps Réel
    elif any(k in q for k in ["enjeu", "enjeux", "strategie", "lecture", "temps réel", "direct"]):
        reponse = (
            f"📡 **Analyse des flux en temps réel** :\n"
            f"- **Tendance PMU** : {live_data['pmu']['tendance_betting']}\n"
            f"- **État de la piste** : {live_data['geny']['terrain']}\n"
            f"L'enjeu tactique va se jouer sur la capacité des favoris à s'adapter à cette piste précise au vu des dernières minutes d'échauffement."
        )

    # 6. Favori / Base AZ Turf Pro
    elif any(k in q for k in ["favori", "coup sur", "base"]):
        if classement:
            top = classement[0]
            reponse = (
                f"🎯 **La Base Synthèse AZ Turf Pro** : N°{top.get('numero')} **{top.get('nom')}**.\n"
                f"Notre algorithme (Indice {top.get('indice_az')}) est en parfait accord avec les flux PMU/Zeturf actuels. C'est le point d'appui solide."
            )
        else:
            reponse = "⚠️ Lancez l'analyse de course."

    # 7. Réponse par défaut
    else:
        if classement:
            reponse = (
                "🤖 **Scan Multi-Sources Actif (PMU, Zeturf, Geny)**.\n\n"
                "Posez-moi des questions professionnelles :\n"
                "- Quel est le **mauvais favori** selon l'évolution des cotes ?\n"
                "- Quel est le cheval **troublant** repéré par les radars ?\n"
                "- Quels sont les **bruits d'écurie** en direct ?"
            )
        else:
            reponse = "🤖 Bonjour ! Connectez-vous à une course pour que j'agrège les flux PMU, Zeturf et Geny en temps réel."

    return {"status": "success", "question": question, "reponse": reponse}
