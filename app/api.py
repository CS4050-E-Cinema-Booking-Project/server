from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware


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

class UserModel(UserBase):
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
models.Base.metadata.create_all(bind=engine)

# Post Movies (create new)
@app.post("/movies/", response_model=MovieModel)
async def add_movie(movie: MovieBase, db: db_dependency):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Get Movies (select)
@app.get("/movies/", response_model=List[MovieModel])
async def get_movies(db: db_dependency, skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies

# Get Movies (select)
@app.get("/movies/{given_id}", response_model=List[MovieModel])
async def get_movies(given_id: int, db: db_dependency, skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).filter_by(id=given_id).offset(skip).limit(limit).all()
    return movies

# Put (or update)
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

# Delete
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
@app.post("/users/", response_model=UserModel)
async def add_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user