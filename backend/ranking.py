def ajouter_raison_az(cheval, position):

    indice = cheval.get("indice_az", 0)


    if position == 1:

        return "⭐ Favori AZ : meilleur indice et profil prioritaire"


    if position <= 3:

        return "🔥 Base solide : régularité et forte chance de podium"


    if position <= 5:

        return "🎯 Chance AZ : potentiel pour intégrer l'arrivée"


    if indice >= 180:

        return "💎 Outsider intéressant : peut surprendre"


    return "⚠️ Coup spéculatif"





def classer_chevaux(chevaux):


    classement = sorted(
        chevaux,
        key=lambda x: x.get("indice_az", 0),
        reverse=True
    )



    for index, cheval in enumerate(classement, start=1):

        cheval["rang"] = index

        cheval["raison"] = ajouter_raison_az(
            cheval,
            index
        )


    return classement
