from pydantic import BaseModel


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
