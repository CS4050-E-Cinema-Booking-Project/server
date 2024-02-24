from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    image = Column(String)
    trailer = Column(String)
    director = Column(String)
    genre = Column(String)


class Theater(Base):
    __tablename__ = 'theaters'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    capacity = Column(Integer)
