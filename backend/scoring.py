def calculer_score_az(cheval):

    score = 0

    criteres = {
        "forme": 5,
        "regularite": 4,
        "gains": 3,
        "jockey": 4,
        "cote": 2,
        "distance": 3,
        "terrain": 2,
        "experience": 2
    }


    for critere, poids in criteres.items():

        try:
            valeur = int(cheval.get(critere, 0))
        except (ValueError, TypeError):
            valeur = 0

        score += valeur * poids


    return score
