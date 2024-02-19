from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    description = Column(String)