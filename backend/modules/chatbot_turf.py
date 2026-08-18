"""
AZ TURF PRO - ASSISTANT CONVERSATIONNEL IA
Fichier : backend/modules/chatbot_turf.py
"""

def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    """
    Répond aux questions de l'utilisateur en s'appuyant sur les données d'analyse courantes.
    """
    q = question.lower().strip()
    moteur = (contexte_analyse or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})

    # 1. Question sur le coup sûr / favori
    if any(k in q for k in ["favori", "coup sur", "meilleur", "gagnant", "top"]):
        if classement:
            top = classement[0]
            reponse = (
                f"🎯 **Le Coup Sûr AZ Turf Pro** est le N°{top.get('numero')} **{top.get('nom')}** "
                f"avec un Indice AZ de **{top.get('indice_az')}** et un Indice Premium de **{top.get('indice_premium')}**."
            )
        else:
            reponse = "Veuillez d'abord lancer une analyse de course pour identifier le favori."

    # 2. Question sur le Quinté / Ticket
    elif any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        quinte_gratuit = (tickets.get("gratuit") or {}).get("quinte", [])
        if quinte_gratuit:
            nums = [str(c.get("numero")) for c in quinte_gratuit]
            reponse = f"💡 **Ticket Quinté Conseillé** : { ' - '.join(nums) }"
        else:
            reponse = "Aucune combinaison Quinté disponible pour le moment."

    # 3. Question sur les Outsiders / Tocards / Smart Money
    elif any(k in q for k in ["outsider", "tocard", "surprise", "pépite", "pepite"]):
        outsiders = [c for c in classement if float(c.get("cote", 0) or 0) >= 10.0]
        if outsiders:
            top_out = outsiders[0]
            reponse = (
                f"🔥 **Outsider à surveiller** : N°{top_out.get('numero')} **{top_out.get('nom')}** "
                f"(Cote : {top_out.get('cote')}). Son Indice Premium de {top_out.get('indice_premium')} indique une belle valeur !"
            )
        else:
            reponse = "Aucun outsider n'a été repéré avec un niveau de confiance suffisant sur cette course."

    # 4. Question sur les Badges
    elif "badge" in q or "signification" in q:
        reponse = (
            "🏷️ **Guide des Badges Intelligents** :\n"
            "- **D4** : Déferré des 4 pieds (Gain de performance net).\n"
            "- **Duo Chaud 🔥** : Jockey & Entraîneur en très haute réussite.\n"
            "- **Spécialiste 🎯** : Cheval très performant sur cet hippodrome.\n"
            "- **Rachat ⚡** : Disqualifié récemment mais avec une cote attirante."
        )

    # 5. Réponse par défaut
    else:
        reponse = (
            "Posez-moi une question sur le favori, la sélection Quinté, "
            "les outsiders de la course ou la signification des badges AZ Turf Pro !"
        )

    return {
        "status": "success",
        "question": question,
        "reponse": reponse
  }
