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
from cryptography.fernet import Fernet

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
    key = Fernet.generate_key() #this is your "password"
    cipher_suite = Fernet(key)
    db_user.password = cipher_suite.encrypt(bytes(db_user.password.encode()))
    db_user.confirmPassword = cipher_suite.encrypt(bytes(db_user.confirmPassword.encode()))
    db_user.key = key
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Get Users (select)
@app.get("/users/", response_model=List[data_models.UserModel])
async def get_users(db: db_dependency, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()    
    for user in users:
        cipher_suite = Fernet(user.key)
        user.password = cipher_suite.decrypt(user.password)
    return users

# Put (or update) User Password
@app.put("/users/{given_id}", tags=["users"])
async def update_password(user: data_models.UserModel, db: db_dependency):
    userNew = db.query(models.User).filter_by(id=user.id).first()
    cipher_suite = Fernet(userNew.key)
    userNew.password = cipher_suite.decrypt(userNew.password)
    if userNew is not None:
        if userNew.password != user.password:
            key = Fernet.generate_key() #this is your "password"
            cipher_suite = Fernet(key)
            userNew.password = cipher_suite.encrypt(bytes(user.password.encode()))
            userNew.confirmPassword = cipher_suite.encrypt(bytes(user.confirmPassword.encode()))
            userNew.key = key
            subject = "Fossil Flicks Password Reset"
            body = "Your password has been reset."
            recipients = [user.email]
            try:
                send_email(subject, body, recipients)
            except:
                Exception

        flag = False
        # Update non-password elements
        if (userNew.firstName != user.firstName or userNew.lastName != user.lastName or userNew.email != user.email or userNew.phoneNumber != user.phoneNumber
            or userNew.streetAddress != user.streetAddress or userNew.city != user.city or userNew.state != user.state or userNew.zipCode != user.zipCode
            or userNew.userCode != user.userCode or userNew.userStatus != user.userStatus or userNew.userType != user.userType or userNew.promotionOptIn != user.promotionOptIn):
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
            userNew.promotionOptIn = user.promotionOptIn

            subject = "Fossil Flicks Account Information Changed"
            body = "Your Account Information has been changed."
            recipients = [user.email]
            try:
                send_email(subject, body, recipients)
            except:
                Exception

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
async def get_promotions(db: db_dependency, skip: int = 0, limit: int = 100):
    promotions = db.query(models.Promotion).offset(skip).limit(limit).all()
    return promotions


# Post Users (create new)
@app.post("/paymentCards/", response_model=data_models.PaymentCardModel)
async def add_card(card: data_models.PaymentCardBase, db: db_dependency):
    key = Fernet.generate_key() #this is your "password"
    cipher_suite = Fernet(key)
    for value in card:
        if value[1] is not None:
            setattr(card, value[0], cipher_suite.encrypt(value[1].encode()))
    card.key = key
    db_card = models.PaymentCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

# Post Users (create new)
@app.get("/paymentCards/", response_model=List[data_models.PaymentCardModel])
async def get_cards(db: db_dependency, skip: int = 0, limit: int = 100):
    cards = db.query(models.PaymentCard).offset(skip).limit(limit).all()
    for card in cards:
        cipher_suite = Fernet(card.key)
        card.userID = cipher_suite.decrypt(card.userID)
        card.cardNumber = cipher_suite.decrypt(card.cardNumber)
        card.expirationDate = cipher_suite.decrypt(card.expirationDate)
        card.cvc = cipher_suite.decrypt(card.cvc)
        card.firstName = cipher_suite.decrypt(card.firstName)
        card.lastName = cipher_suite.decrypt(card.lastName)
        card.streetAddress = cipher_suite.decrypt(card.streetAddress)
        card.city = cipher_suite.decrypt(card.city)
        card.state = cipher_suite.decrypt(card.state)
        card.zipCode = cipher_suite.decrypt(card.zipCode)
        
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
    user = db.query(models.User).filter_by(id=card.userID).first()
    if cardNew is not None:
        # Update non-password elements
        key = cardNew.key
        cipher_suite = Fernet(key)
        cardNew.cardNumber = cipher_suite.encrypt(card.cardNumber.encode())
        cardNew.expirationDate = cipher_suite.encrypt(card.expirationDate.encode())
        cardNew.cvc = cipher_suite.encrypt(card.cvc.encode())
        cardNew.firstName = cipher_suite.encrypt(card.firstName.encode())
        cardNew.lastName = cipher_suite.encrypt(card.lastName.encode())
        cardNew.streetAddress = cipher_suite.encrypt(card.streetAddress.encode())
        cardNew.city = cipher_suite.encrypt(card.city.encode())
        cardNew.state = cipher_suite.encrypt(card.state.encode())
        cardNew.zipCode = cipher_suite.encrypt(card.zipCode.encode())

        subject = "Fossil Flicks Account Billing Information Changed"
        body = "Your Account Billing Information has been changed."
        recipients = [user.email]
        try:
            send_email(subject, body, recipients)
        except:
            Exception

        db.commit()
        db.refresh(cardNew)
        return cardNew

    return {
        "data": f"User with id {card.id} not found."
    }