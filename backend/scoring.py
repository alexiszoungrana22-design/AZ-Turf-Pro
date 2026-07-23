def calculer_score_az(cheval):
    score = 0

    score += cheval.get("forme", 0) * 5
    score += cheval.get("regularite", 0) * 4
    score += cheval.get("gains", 0) * 3
    score += cheval.get("jockey", 0) * 4
    score += cheval.get("cote", 0) * 2

    return score
