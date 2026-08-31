
"""
Score expert complémentaire.
Le score AZ original reste indépendant.
"""

def calculer_score_expert(
    indice_az=0,
    forme=0,
    cote=0,
    terrain=0,
    jockey=0,
    presse=0
):
    score = (
        indice_az * 0.40 +
        forme * 0.20 +
        cote * 0.15 +
        terrain * 0.10 +
        jockey * 0.10 +
        presse * 0.05
    )
    return round(score, 2)
