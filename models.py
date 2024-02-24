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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String)
    phoneNumber = Column(String)
    password = Column(String)
    confirmPassword = Column(String)
