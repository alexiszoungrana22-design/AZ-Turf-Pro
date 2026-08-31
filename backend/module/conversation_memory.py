
from dataclasses import dataclass, field
@dataclass
class State:
    last_horses: list = field(default_factory=list)
    last_analysis: dict = field(default_factory=dict)
    last_tickets: dict = field(default_factory=dict)
    last_intent: str = ""
def remember(state, intent=None, horses=None, analysis=None, tickets=None):
    if intent: state.last_intent = intent
    if horses: state.last_horses = horses
    if analysis is not None: state.last_analysis = analysis
    if tickets is not None: state.last_tickets = tickets
    return state
