from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models

app = FastAPI()

class MovieBase(BaseModel):
    id: int
    name: str

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


origins = [
    "http://localhost:3000",
    "localhost:3000"
]

movies = [
    {
        "id": "1",
        "item": "Shawshank Redemption"
    },
    {
        "id": "2",
        "item": "Inception"
    },
    {
        "id": "3",
        "item": "Troy"
    }
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Get Movies (select)
@app.get("/movie", tags=["movies"])#, response_model=List[MovieModel])
async def get_movies(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> dict:
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    movies_data = [{"id":str(x.id),"item":x.name} for x in movies]
    return { "data": movies_data }

# Post Movies (create new)
@app.post("/movie", tags=["movies"])#, response_model=List[MovieModel])
async def add_movie(movie: dict, db: Session = Depends(get_db)) -> dict:
    db_movie = models.Movie(id = movie['id'], name = movie['item'])
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Root
@app.get("/",tags=["root"])
async def read_root() -> dict:
    return {"message":"Welcome to your movie list."}






# Put (or update)
@app.put("/movie/{id}", tags=["movies"])
async def update_movie(id: int, body: dict) -> dict:
    for movie in movies:
        if int(movie["id"]) == id:
            movie["item"] = body["item"]
            return {
                "data": f"Movie with id {id} has been updated."
            }

    return {
        "data": f"Movie with id {id} not found."
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
        "data": f"Movie with id {id} not found."
    }


@app.post("/movies_db/", response_model=MovieModel)
async def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie



@app.get("/movies_db/", response_model=List[MovieModel])
async def read_movies(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies
