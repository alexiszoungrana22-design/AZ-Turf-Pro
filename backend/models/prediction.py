from sqlalchemy import Column, Integer, String, Float

from models.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    race_id = Column(Integer)

    selected_horses = Column(String)

    base_az = Column(String)

    cheval_piege = Column(String)

    indice_az = Column(
        Float,
        default=0
    )

    commentaire = Column(String)
