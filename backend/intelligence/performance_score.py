def calculer_score(stats):
    if not stats: return 0
    return round(float(stats.get('precision',0))*0.5+float(stats.get('valeur',0))*0.3+float(stats.get('analyse',0))*0.2,2)
