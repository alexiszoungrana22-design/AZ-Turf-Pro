from sqlalchemy import Column, Integer, String

from models.database import Base


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(String)

    hippodrome = Column(String)

    race_name = Column(String)

    distance = Column(String)

    type_course = Column(String)

    status = Column(
        String,
        default="Analyse en cours"
    )
