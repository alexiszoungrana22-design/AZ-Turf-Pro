from pydantic import BaseModel


class Cheval(BaseModel):

    numero:int
    score:float
