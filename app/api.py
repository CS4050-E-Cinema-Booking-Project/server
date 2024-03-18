from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import data_models
from app.utils.send_email import send_email
from random import randint

app = FastAPI()

origins = [
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials= True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
models.Base.metadata.create_all(bind=engine)

# Post Movies (create new)
@app.post("/movies/", response_model=data_models.MovieModel)
async def add_movie(movie: data_models.MovieBase, db: db_dependency):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


# Get All Movies (select)
@app.get("/movies/", response_model=List[data_models.MovieModel])
async def get_movies(db: db_dependency, skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies

# Get Specific Movie (select)
@app.get("/movies/{given_id}", response_model=List[data_models.MovieModel])
async def get_movies(given_id: int, db: db_dependency, skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).filter_by(id=given_id).offset(skip).limit(limit).all()
    return movies

# Put (or update) Movie
@app.put("/movies/{given_id}", tags=["movies"])
async def update_movie(
    body: dict,
    db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter_by(id=body['given_id']).first()
    if movie is not None:
        movie.title = body['given_title']
        movie.description = body['given_desc']
        db.commit()
        db.refresh(movie)
        return movie

    return {
        "data": f"Movie with id {body['given_id']} not found."
    }

# Delete Movie
@app.delete("/movies/{given_id}", tags=["movies"])
async def delete_movie(given_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter_by(id=given_id).first()
    if movie is not None:
        db.delete(movie)
        db.commit()
        return movie
    
    return {
        "data": f"Movie with id {given_id} not found."
    }


# Post Users (create new)
@app.post("/users/send-confirmation-email", response_model=data_models.UserModel)
async def add_user(user: data_models.UserBase, db: db_dependency):
    subject = "Fossil Flicks Account Confirmation"
    userCode = str(randint(10000,99999))
    body = "Please Enter the following code to confirm your account: \n" + str(userCode)
    recipients = [user.email]
    
    try:
        send_email(subject, body, recipients)
    except:
        Exception
    db_user = models.User(**user.dict())
    db_user.userCode = userCode
    db_user.id = -1
    return db_user

# Post Users (create new)
@app.post("/users/", response_model=data_models.UserModel)
async def add_user(user: data_models.UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Get Users (select)
@app.get("/users/", response_model=List[data_models.UserModel])
async def get_users(db: db_dependency, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Put (or update) User Password
@app.put("/users/{given_id}", tags=["users"])
async def update_password(user: data_models.UserModel, db: db_dependency):
    userNew = db.query(models.User).filter_by(id=user.id).first()
    if userNew is not None:
        if userNew.password != user.password:
            userNew.password = user.password
            userNew.confirmPassword = user.confirmPassword
            subject = "Fossil Flicks Password Reset"
            body = "Your password has been reset."
            recipients = [user.email]
            try:
                send_email(subject, body, recipients)
            except:
                Exception

        # Update non-password elements
        userNew.firstName = user.firstName
        userNew.lastName = user.lastName
        userNew.email = user.email
        userNew.phoneNumber = user.phoneNumber
        userNew.streetAddress = user.streetAddress
        userNew.city = user.city
        userNew.state = user.state
        userNew.zipCode = user.zipCode
        userNew.userCode = user.userCode
        userNew.userStatus = user.userStatus
        userNew.userType = user.userType

        db.commit()
        db.refresh(userNew)
        return userNew

    return {
        "data": f"User with id {user.id} not found."
    }

# Post Users (create new)
@app.post("/users/resend-email", response_model=data_models.UserModel)
async def resend_email(user: data_models.UserBase, db: db_dependency):
    subject = "Fossil Flicks Account Confirmation (Resent)"
    body = "(RESENT EMAIL) Please Enter the following code to confirm your account: \n" + str(user.userCode)
    recipients = [user.email]
    
    try:
        send_email(subject, body, recipients)
        print("Email Resent")
    except:
        Exception
    db_user = models.User(**user.dict())
    db_user.id = -1 # Fake id so validation doesn't break
    return db_user

# Post Users (create new)
@app.post("/users/reset-password/", response_model=data_models.UserModel)
async def reset_password(user: data_models.UserModel, db: db_dependency):#user_code, user_email):
    subject = "Fossil Flicks Forgot Password"
    userId = user.id
    body = "Please navigate to the following link to reset your password: \n" + "http://localhost:3000/reset-password/" + str(userId)
    recipients = [user.email]
    
    try:
        send_email(subject, body, recipients)
        print("Email Resent")
    except:
        Exception
    db_user = models.User(**user.dict())
    db_user.id = -1 # Fake id so validation doesn't break
    return db_user



# Get Promotions (select)
@app.get("/promotions/", response_model=List[data_models.PromotionModel])
async def get_users(db: db_dependency, skip: int = 0, limit: int = 100):
    promotions = db.query(models.Promotion).offset(skip).limit(limit).all()
    return promotions


# Post Users (create new)
@app.post("/paymentCards/", response_model=data_models.PaymentCardModel)
async def add_card(card: data_models.PaymentCardBase, db: db_dependency):
    db_card = models.PaymentCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

# Post Users (create new)
@app.get("/paymentCards/", response_model=List[data_models.PaymentCardModel])
async def get_cards(db: db_dependency, skip: int = 0, limit: int = 100):
    cards = db.query(models.PaymentCard).offset(skip).limit(limit).all()
    return cards

# Get Users (select)
@app.get("/paymentCards/{given_id}", response_model=data_models.PaymentCardModel)
async def get_payment_info(given_id: int, db: db_dependency, skip: int = 0, limit: int = 100):
    card = db.query(models.PaymentCard).filter_by(userID=given_id).first()
    if card is not None:
        return card
    else:
        return {"data": f"User with id {given_id} not found."}


# Put (or update) User Password
@app.put("/paymentCards/{given_id}", tags=["paymentCards"])
async def update_card(card: data_models.PaymentCardModel, db: db_dependency):
    cardNew = db.query(models.PaymentCard).filter_by(id=card.id).first()
    if cardNew is not None:
        # Update non-password elements
        cardNew.cardNumber = card.cardNumber
        cardNew.expirationDate = card.expirationDate
        cardNew.cvc = card.cvc
        cardNew.firstName = card.firstName
        cardNew.lastName = card.lastName
        cardNew.streetAddress = card.streetAddress
        cardNew.city = card.city
        cardNew.state = card.state
        cardNew.zipCode = card.zipCode

        db.commit()
        db.refresh(cardNew)
        return cardNew

    return {
        "data": f"User with id {card.id} not found."
    }