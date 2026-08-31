
import re
def route(question, state=None):
    q=(question or "").lower()
    refs=[int(x) for x in re.findall(r"\b\d{1,2}\b", q)]
    if any(x in q for x in ("pourquoi","explique","raison")): intent="explanation"
    elif any(x in q for x in ("compare","entre","vs","versus")): intent="comparison"
    elif any(x in q for x in ("et si","scénario","scenario")): intent="scenario"
    elif any(x in q for x in ("ticket","quinté","quinte","quarté","quarte","trio","couplé","couple")): intent="ticket"
    elif any(x in q for x in ("actualité","actualite","news","dernière minute","derniere minute")): intent="news"
    elif any(x in q for x in ("analyse","pronostic","prono","favori","outsider","base")): intent="analysis"
    else: intent="general"
    if not refs and state and any(x in q for x in ("celui-là","celui la","ce cheval","le précédent")):
        refs=state.last_horses[-1:]
    return {"intent":intent,"references":refs}
