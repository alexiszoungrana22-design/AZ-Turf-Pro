"""AZ TURF PRO - ASSISTANT CONVERSATIONNEL IA"""

def repondre_assistant_turf(question: str, contexte_analyse: dict = None) -> dict:
    q = question.lower().strip()
    moteur = (contexte_analyse or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})

    if any(k in q for k in ["favori", "coup sur", "meilleur", "gagnant", "top"]):
        if classement:
            top = classement[0]
            reponse = (
                f"🎯 **Le Coup Sûr AZ Turf Pro** est le N°{top.get('numero')} "
                f"**{top.get('nom')}** avec un Indice AZ de **{top.get('indice_az')}** "
                f"et un Indice Premium de **{top.get('indice_premium')}**."
            )
        else:
            reponse = "Veuillez d'abord lancer une analyse de course pour identifier le favori."
    elif any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        quinte = (tickets.get("gratuit") or {}).get("quinte", [])
        if quinte:
            nums = [str(c.get("numero")) for c in quinte]
            reponse = "💡 **Ticket Quinté Conseillé** : " + " - ".join(nums)
        else:
            reponse = "Aucune combinaison Quinté disponible pour le moment."
    elif any(k in q for k in ["outsider", "tocard", "surprise", "pépite", "pepite"]):
        outsiders = [c for c in classement if float(c.get("cote", 0) or 0) >= 10.0]
        if outsiders:
            c = outsiders[0]
            reponse = f"🔥 **Outsider à surveiller** : N°{c.get('numero')} **{c.get('nom')}** (Cote : {c.get('cote')})."
        else:
            reponse = "Aucun outsider n'a été repéré avec un niveau de confiance suffisant."
    elif "badge" in q or "signification" in q:
        reponse = ("🏷️ **Guide des Badges** :\n- **D4** : Déferré des 4 pieds.\n"
                   "- **Duo Chaud 🔥** : Jockey & entraîneur en réussite.\n"
                   "- **Spécialiste 🎯** : aptitude détectée.\n"
                   "- **Rachat ⚡** : profil à reconsidérer.")
    else:
        reponse = "Posez-moi une question sur le favori, la sélection Quinté, les outsiders ou les badges AZ Turf Pro !"

    return {"status": "success", "question": question, "reponse": reponse}
