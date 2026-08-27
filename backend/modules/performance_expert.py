
"""
Statistiques de performance Expert V4
"""

def statistiques_expert(historique):
    total = len(historique)

    if total == 0:
        return {
            "courses": 0,
            "indice_confiance": 0
        }

    trouves = sum(
        1 for h in historique
        if h.get("nombre_trouves", 0) >= 3
    )

    return {
        "courses": total,
        "indice_confiance": round((trouves / total) * 100, 1)
    }
