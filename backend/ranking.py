def classer_chevaux(chevaux):

    if not isinstance(chevaux, list):
        return []


    classement = sorted(
        chevaux,
        key=lambda x: (
            x.get("score", 0),
            x.get("regularite", 0),
            x.get("forme", 0)
        ),
        reverse=True
    )


    for rang, cheval in enumerate(classement, start=1):
        cheval["rang"] = rang


    return classement
