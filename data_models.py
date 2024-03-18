from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pydantic.schema import Optional
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware


class MovieBase(BaseModel):
    title: str
    description: str
    image: str
    trailer: str
    director: str
    genre: str
    releaseDate: str

class MovieModel(MovieBase):
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True 

class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    password: str
    confirmPassword: str
    streetAddress: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipCode: Optional[str]
    userCode: Optional[str]
    userStatus: Optional[str]
    userType: Optional[str]
    promotionOptIn: Optional[str]
    key: Optional[str]

class UserModel(UserBase):
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True 

class PromotionBase(BaseModel):
    description = str
    status = str

class PromotionModel(UserBase):
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True 


class PaymentCardBase(BaseModel):
    userID: Optional[str]
    cardNumber: Optional[str]
    expirationDate: Optional[str]
    cvc: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    streetAddress: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipCode: Optional[str]
    key: Optional[str]

class PaymentCardModel(PaymentCardBase):
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True 