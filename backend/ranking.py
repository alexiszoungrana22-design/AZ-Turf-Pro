def classer_chevaux(chevaux):

    if not isinstance(chevaux, list):
        return []


    classement = sorted(
        chevaux,
        key=lambda cheval: cheval.get("indice_az", 0),
        reverse=True
    )


    for rang, cheval in enumerate(classement, start=1):
        cheval["rang"] = rang


    return classement
