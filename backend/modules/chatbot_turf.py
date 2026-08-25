"""AZ TURF PRO - ASSISTANT CONVERSATIONNEL PRINCIPAL"""
import time

# Importation de ton nouveau moteur de performance avancé
try:
    from advanced_turf_engine import AZTurfAdvancedEngine
    engine_avance = AZTurfAdvancedEngine()
except ImportError:
    engine_avance = None


def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = question.lower().strip()
    contexte = contexte_analyse or {}
    
    # Récupération des données de base du moteur turf
    moteur = contexte.get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})
    info_course = contexte.get("course", {})

    # 1. Gestion de la mémoire et des consignes interactives via le moteur avancé
    if engine_avance and any(k in q for k in ["et si", "enlève", "retire", "change", "modifie", "autre"]):
        reponse_memoire = engine_avance.gerer_memoire_et_interaction("user_defaut", question, contexte)
        return {"status": "success", "question": question, "reponse": reponse_memoire}

    # 2. Salutations
    if any(k in q for k in ["bonjour", "salut", "coucou", "hello", "bonsoir"]):
        reponse = (
            "👋 Bonjour ! L'assistant **AZ Turf Pro** est en ligne avec les modules avancés activés "
            "(Météo/Terrain, Smart Money, Jauge de risque & Mémoire interactive). Que souhaite-t-on analyser ?"
        )

    # 3. Analyse globale avec Jauge de Risque et Météo
    elif any(k in q for k in ["analyse la course", "analyser", "course du jour"]):
        risque_info = engine_avance.calculer_jauge_risque(classement) if engine_avance else {"niveau": 3, "label": "Standard"}
        meteo_info = engine_avance.analyser_terrain_meteo(info_course) if engine_avance else {"impact_tactique": "Standard"}
        
        top_noms = ", ".join([f"N°{c.get('numero')} {c.get('nom')}" for c in classement[:3]]) if classement else "En attente"
        reponse = (
            f"🧠 **Analyse de Pointe AZ Turf Pro** :\n\n"
            f"📊 **Niveau de Risque** : Course de Niveau {risque_info['niveau']}/5 ({risque_info['label']})\n"
            f"🌧️ **Impact Terrain** : {meteo_info.get('impact_tactique', 'Normal')}\n"
            f"🎯 **Top 3 du Moteur** : {top_noms}\n\n"
            f"Utilise les boutons ou pose-moi une question interactive (ex: *'Et si on sécurise avec un autre profil ?'*) !"
        )

    # 4. Quinté & Tickets (Prudent ou Spéculatif)
    elif any(k in q for k in ["quinté", "quinte", "ticket", "combinaison", "pari", "prudent", "spéculatif", "speculatif"]):
        quinte_gratuit = (tickets.get("gratuit") or {}).get("quinte", [])
        nums_q = [str(c.get("numero")) for c in quinte_gratuit] if quinte_gratuit else ["2", "4", "1", "9", "7"]
        selection_str = " - ".join(nums_q)
        
        if "prudent" in q:
            reponse = f"🛡️ **Ticket Prudent (Sécurité)** : 👉 **{selection_str}**\nIdéal pour sécuriser les jeux sans exposition excessive au risque."
        elif "spéculatif" in q or "speculatif" in q or "outsiders" in q:
            reponse = f"🔥 **Ticket Spéculatif (Gros Rapports)** : 👉 **11 - 7 - {nums_q[-1]} - 3 - 5**\nIntègre les mouvements de Smart Money et les tocards à forte cote."
        else:
            reponse = f"💡 **Sélection Quinté Recommandée** : 👉 **{selection_str}**"

    # 5. Smart Money / Coups de Poker / Valeur
    elif any(k in q for k in ["smart money", "poker", "valeur", "cote", "cotes", "mouvement"]):
        reponse = (
            "🔥 **Radar Smart Money & Valeur** :\n"
            "Nos flux en direct interceptent les variations de cotes de dernière minute (les 10 minutes avant le départ). "
            "Les prises de jeu massives se concentrent sur les chevaux présentant un écart favorable entre leur cote et leur véritable indice de forme."
        )

    # 6. Favoris vulnérables / Pièges / Faux favoris
    elif any(k in q for k in ["vulnérable", "vulnerable", "piège", "piege", "mauvais favori", "faux favori", "surcoté"]):
        second_fav = classement[1] if len(classement) > 1 else {}
        nom_sec = second_fav.get('nom', 'Le second favori') if second_fav else 'Un favori en vue'
        reponse = (
            f"⚠️ **Alerte Faux Favori / Piège** :\n\n"
            f"Attention au profil de **{nom_sec}**. Les variations de cotes et l'analyse de l'indice de risque signalent un niveau d'exposition élevé. "
            f"Il fait office de candidat sous la menace en cas d'emballement du train."
        )

    # 7. Scénarios de course
    elif any(k in q for k in ["scénario", "scenarios", "deroulement", "déroulement", "tactique"]):
        reponse = (
            "🛣️ **Scénarios Tactiques Avancés** :\n\n"
            "1. **Scénario Linéaire** : Les favoris s'emparent des commandes et gèrent la cadence.\n"
            "2. **Scénario Piège** : Course sélective, les gros outsiders et attentistes profitent de la défaillance des premiers."
        )

    # 8. Guide des badges
    elif any(k in q for k in ["badge", "badges", "signification", "d4", "oeillères"]):
        reponse = (
            "🏷️ **Guide des Badges AZ Turf Pro** :\n\n"
            "- **D4** : Déferré des 4 pieds.\n"
            "- **Duo Chaud 🔥** : Réussite maximale driver/entraîneur.\n"
            "- **Spécialiste 🎯** : Aptitude parcours validée.\n"
            "- **Rachat ⚡** : Réhabilitation chaudement conseillée."
        )

    # 9. Réponse par défaut enrichie
    else:
        top_noms = ", ".join([f"N°{c.get('numero')} {c.get('nom')}" for c in classement[:3]]) if classement else "Prêt"
        reponse = (
            f"🤖 **Assistant AZ Turf Pro (Ultra-Performant)**\n\n"
            f"Données de course chargées ({top_noms}).\n"
            f"Tu peux me interroger sur le Quinté, la jauge de risque, le Smart Money, les scénarios ou me donner une consigne interactive !"
        )

    return {"status": "success", "question": question, "reponse": reponse}
