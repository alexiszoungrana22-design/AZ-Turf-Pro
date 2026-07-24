from pydantic import BaseModel


class Cheval(BaseModel):

    numero: int

    nom: str = ""

    forme: int = 0

    regularite: int = 0

    gains: int = 0

    jockey: int = 0

    cote: int = 0

    distance: int = 0

    terrain: int = 0

    experience: int = 0

    score: float = 0
