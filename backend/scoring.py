def calculer_score_az(cheval):

    score = 0

    # Forme récente (priorité)
    score += cheval.get("forme", 0) * 5

    # Régularité
    score += cheval.get("regularite", 0) * 4

    # Classe / gains
    score += cheval.get("gains", 0) * 3

    # Jockey ou driver
    score += cheval.get("jockey", 0) * 4

    # Cote (indice de confiance marché)
    score += cheval.get("cote", 0) * 2

    # Nouveaux critères AZ
    score += cheval.get("distance", 0) * 3
    score += cheval.get("terrain", 0) * 2
    score += cheval.get("experience", 0) * 2

    return score
