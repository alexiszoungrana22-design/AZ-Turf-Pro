"""Consensus presse : exploite uniquement les pronostics réellement fournis."""
def analyser_consensus_presse(data: dict) -> dict:
    pronostics = (data or {}).get("pronostics") or []
    if not isinstance(pronostics, list) or not pronostics:
        return {"status":"warning", "consensus":[], "source":"aucune_donnee_presse"}
    votes = {}
    for source in pronostics:
        nums = source.get("selection") if isinstance(source, dict) else source
        if isinstance(nums, str):
            nums = nums.replace(",", " ").split()
        if not isinstance(nums, list):
            continue
        for n in nums:
            try: n = str(int(n))
            except Exception: continue
            votes[n] = votes.get(n, 0) + 1
    consensus = sorted(({"numero":n,"votes":v} for n,v in votes.items()), key=lambda x:(-x["votes"], int(x["numero"])))
    return {"status":"success", "consensus":consensus, "sources":len(pronostics)}
