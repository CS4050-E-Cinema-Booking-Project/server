from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)