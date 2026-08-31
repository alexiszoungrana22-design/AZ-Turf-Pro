
"""
Calcul complémentaire.
Le score AZ original n'est pas modifié.
"""

def score_expert(
    az=0,
    forme=0,
    marche=0,
    terrain=0,
    jockey=0,
    presse=0
):
    return round(
        az*0.40 +
        forme*0.20 +
        marche*0.15 +
        terrain*0.10 +
        jockey*0.10 +
        presse*0.05,
        2
    )
