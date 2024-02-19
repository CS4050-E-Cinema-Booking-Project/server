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
    item: str
    description: str

class MovieModel(MovieBase):
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

# Put (or update)
@app.put("/movie/{given_id}", tags=["movies"])
async def update_movie(
    given_id: int,
    given_name: str,
    given_price: float,
    db: Session = Depends(get_db)) -> dict:
    movie = db.query(models.Movie).filter_by(id=given_id).first()
    if movie is not None:
        movie.name = given_name
        movie.price = given_price
        db.commit()
        db.refresh(movie)
        return movie

    return {
        "data": f"Movie with id {given_id} not found."
    }

# Delete
@app.delete("/movie/{given_id}", tags=["movies"])
async def delete_movie(given_id: int, db: Session = Depends(get_db)) -> dict:
    movie = db.query(models.Movie).filter_by(id=given_id).first()
    if movie is not None:
        db.delete(movie)
        db.commit()
        return movie
    
    return {
        "data": f"Movie with id {given_id} not found."
    }
