def calculer_score_az(cheval):

    score = 0


    # Forme récente (critère majeur)
    score += cheval.get(
        "forme",
        0
    ) * 5



    # Régularité
    score += cheval.get(
        "regularite",
        0
    ) * 4



    # Gains / classe du cheval
    score += cheval.get(
        "gains",
        0
    ) * 3



    # Jockey / driver
    score += cheval.get(
        "jockey_score",
        0
    ) * 4



    # Cote marché
    score += cheval.get(
        "cote",
        0
    ) * 2



    # Adaptation distance
    score += cheval.get(
        "distance",
        0
    ) * 3



    # Adaptation terrain
    score += cheval.get(
        "terrain",
        0
    ) * 2



    # Expérience
    score += cheval.get(
        "experience",
        0
    ) * 2



    # Bonus performances récentes
    performances = cheval.get(
        "performances",
        []
    )


    if performances:


        bonnes_places = 0


        for place in performances:


            if place <= 3:

                bonnes_places += 1



        score += bonnes_places * 5



    return score
