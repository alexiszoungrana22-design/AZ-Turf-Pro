
"""Façade d'intégration non destructive."""
from .intent_router import route
from .autonomous_reasoning import analyze_independently, make_tickets, compare_to_az
from .conversation_memory import State, remember

def repondre(question, contexte=None, state=None):
    contexte=contexte or {}
    state=state or State()
    routed=route(question, state)
    result=analyze_independently(contexte)
    tickets=make_tickets(result)
    remember(state, routed["intent"], routed["references"], result, tickets)
    return {
        "intent": routed["intent"],
        "independent_analysis": result,
        "independent_tickets": tickets,
        "comparison_az": compare_to_az(result, contexte),
        "state": state,
    }
