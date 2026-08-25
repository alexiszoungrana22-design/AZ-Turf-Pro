def analyser_consensus_presse(data: dict) -> dict:
    info = (data or {}).get("info_course") or {}
    chevaux = (data or {}).get("chevaux") or []
    plus_joues = info.get("plus_joues") or []

    consensus = []
    for item in plus_joues:
        if isinstance(item, dict):
            num = item.get("numero")
            nom = item.get("nom", "")
            if num is not None:
                consensus.append({"numero": str(num), "nom": nom, "source": "plus_joues"})
        else:
            consensus.append({"numero": str(item), "nom": "", "source": "plus_joues"})

    if not consensus:
        # Fallback uniquement sur les partants déjà fournis, sans inventer une source presse.
        top = sorted(
            [c for c in chevaux if isinstance(c, dict)],
            key=lambda c: float(c.get("indice_az", c.get("indice", 0)) or 0),
            reverse=True,
        )[:3]
        consensus = [
            {"numero": str(c.get("numero")), "nom": c.get("nom", ""), "source": "classement_interne"}
            for c in top if c.get("numero") is not None
        ]

    return {
        "status": "success",
        "consensus": consensus,
        "source": "plus_joues" if plus_joues else "classement_interne",
    }
