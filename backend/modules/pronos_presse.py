"""
Consensus presse : exploite uniquement les sélections de presse déjà présentes
dans les données d'entrée. Aucun pronostic externe n'est fabriqué.
"""


def analyser_consensus_presse(data: dict) -> dict:
    info = (data or {}).get("info_course") or {}
    selections = (
        info.get("presse")
        or info.get("pronostics_presse")
        or info.get("selection_presse")
        or []
    )

    if not selections:
        return {
            "status": "success",
            "consensus": [],
            "source": "aucune_donnee_presse",
            "message": "Aucune sélection presse fournie."
        }

    compte = {}
    for item in selections:
        nums = item if isinstance(item, list) else [item]
        for numero in nums:
            key = str(numero).strip()
            if key:
                compte[key] = compte.get(key, 0) + 1

    consensus = [
        {"numero": numero, "mentions": mentions}
        for numero, mentions in sorted(
            compte.items(), key=lambda x: (-x[1], int(x[0]) if x[0].isdigit() else 9999)
        )
    ]

    return {
        "status": "success",
        "consensus": consensus,
        "source": "donnees_course",
        "message": "Consensus calculé à partir des sélections presse fournies."
    }
