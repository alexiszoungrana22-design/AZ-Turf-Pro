def calcul_score(
    forme,
    regularite,
    jockey,
    distance
):

    score = (
        forme * 0.4 +
        regularite * 0.3 +
        jockey * 0.2 +
        distance * 0.1
    )

    return round(score,2)
