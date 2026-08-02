# =====================================
# AZ TURF PRO
# MODELS
# Cheval + Premium
# =====================================

from typing import Optional
from pydantic import BaseModel


# =====================================
# MODELE CHEVAL
# =====================================

class Cheval(BaseModel):

    numero: int

    nom: str = ""

    age: int = 0

    sexe: str = ""

    jockey: str = ""

    entraineur: str = ""

    forme: int = 0

    regularite: int = 0

    gains: int = 0

    cote: float = 0

    distance: int = 0

    terrain: int = 0

    experience: int = 0

    performances: list = []

    score: float = 0


# =====================================
# MODELE DEMANDE ABONNEMENT
# =====================================

class AbonnementRequest(BaseModel):

    telephone: str

    offre: str

    prix: int

    duree: int

    paiement: str

    # La référence est renseignée plus tard
    # dans activation.html
    reference: Optional[str] = None


# =====================================
# MODELE ACTIVATION PREMIUM
# =====================================

class ActivationRequest(BaseModel):

    telephone: str

    reference: str
