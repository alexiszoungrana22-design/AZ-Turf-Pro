def classer_chevaux(chevaux):

    return sorted(
        chevaux,
        key=lambda x: x["score"],
        reverse=True
    )
