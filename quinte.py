# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# =====================================


def _valides(classement):
    if not isinstance(classement, list):
        return []
    return [c for c in classement if isinstance(c, dict) and c.get("numero") is not None]


def _numero(c):
    return str(c.get("numero"))


def _score(c, cle):
    try:
        return float(c.get(cle, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _uniques(seq):
    resultat=[]
    vus=set()
    for x in seq:
        sx=str(x)
        if sx not in vus:
            vus.add(sx)
            resultat.append(sx)
    return resultat


def generer_champ_reduit(classement):
    numeros=[_numero(c) for c in _valides(classement)]
    if len(numeros)<3:
        return {"format":"", "bases":[], "complements":[], "disponible":False}
    bases=[numeros[0], numeros[1], "X", numeros[2], "X"]
    complements=numeros[3:7]
    fmt="-".join(bases)
    if complements:
        fmt += " / " + "-".join(complements)
    return {"format":fmt,"bases":bases,"complements":complements,"disponible":True}


def generer_ticket_derniere_minute(classement):
    valides=_valides(classement)
    def score(c):
        # Marché + forme + régularité : volontairement indépendant
        # du classement Premium pour éviter une copie automatique.
        cote=_score(c,"cote")
        forme=_score(c,"forme")
        reg=_score(c,"regularite")
        return cote*2.0 + forme*1.2 + reg*0.8
    ordre=sorted(valides,key=score,reverse=True)
    selection=[_numero(c) for c in ordre[:6]]
    joker=_numero(ordre[6]) if len(ordre)>6 else None
    return {"selection":selection,"joker":joker,"format":"-".join(selection)}


def generer_tickets_az(classement):
    valides=_valides(classement)
    if not valides:
        return {"gratuit":{},"premium":{}}

    # GRATUIT = classement AZ pur.
    ordre_az=sorted(valides,key=lambda c:_score(c,"indice_az"),reverse=True)
    az=[_numero(c) for c in ordre_az]

    # PREMIUM = indice Premium, conservé par engine.py.
    ordre_premium=sorted(valides,key=lambda c:_score(c,"indice_premium"),reverse=True)
    premium=[_numero(c) for c in ordre_premium]

    # Sélection Premium de 8 chevaux avec diversification :
    # top Premium + chevaux de valeur hors du noyau gratuit.
    selection=[]
    positions=(0,1,3,5,2,4,6,7)
    for pos in positions:
        if pos < len(premium) and premium[pos] not in selection:
            selection.append(premium[pos])
    for n in premium:
        if n not in selection:
            selection.append(n)
    selection=selection[:8]

    # Garantit que le Quinté Premium ne soit pas une copie du Gratuit.
    quinte_premium=selection[:6]
    if len(az)>=6 and quinte_premium == az[:6]:
        remplacement=next((n for n in premium[6:] if n not in quinte_premium),None)
        if remplacement:
            quinte_premium[-1]=remplacement
    quinte_premium=_uniques(quinte_premium)[:6]

    quarte=quinte_premium[:5]
    trio=quinte_premium[:3]

    couples=[]
    if len(quinte_premium)>=3:
        a,b,c=quinte_premium[:3]
        couples=[[a,b],[a,c],[b,c]]

    champ=generer_champ_reduit(ordre_premium)
    derniere=generer_ticket_derniere_minute(valides)

    # Si la dernière minute recopie exactement le Quinté Premium,
    # on décale d'un rang dans son propre ordre quand c'est possible.
    if derniere["selection"] == quinte_premium and len(valides)>6:
        candidats=[_numero(c) for c in sorted(valides,key=lambda c:(_score(c,"cote")*2+_score(c,"forme")*1.2+_score(c,"regularite")*.8),reverse=True)]
        alt=next((n for n in candidats if n not in quinte_premium),None)
        if alt:
            derniere["selection"][-1]=alt
            derniere["format"]="-".join(derniere["selection"])

    gratuit={
        "quinte":az[:7],
        "deux_sur_quatre":az[:4],
        "couple_place":az[:2],
    }

    premium_data={
        "selection_quinte":selection,
        "quinte":quinte_premium,
        "quarte":quarte,
        "trio":trio,
        "couple_gagnant_place":couples,
        "champ_reduit":champ,
        "ticket_derniere_minute":derniere,
        "methode":"Indice Premium AZ Pro : valeur + forme + régularité + expérience, avec diversification des tickets.",
        "message_fin":"🍀 Bonne chance ! Les tickets Premium sont générés séparément du ticket gratuit et la dernière minute est calculée indépendamment.",
    }

    return {"gratuit":gratuit,"premium":premium_data}
    
