from sqlalchemy import Column, Integer, String, Float

from models.database import Base


class Horse(Base):
    __tablename__ = "horses"

    id = Column(Integer, primary_key=True, index=True)

    number = Column(Integer)
    name = Column(String)

    age = Column(Integer)
    trainer = Column(String)
    jockey = Column(String)

    last_results = Column(String)

    az_score = Column(Float, default=0)

    category = Column(
        String,
        default="A analyser"
    )
