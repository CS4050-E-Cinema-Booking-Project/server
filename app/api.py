from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
@app.get("/movie", tags=["movies"])
async def get_movies() -> dict:
    return { "data": movies }

# Post Movies (create new)
@app.post("/movie", tags=["movies"])
async def add_movie(movie: dict) -> dict:
    movies.append(movie)
    return {
        "data": { "Movie added." }
    }

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
@app.delete("/movie/{id}", tags=["movies"])
async def delete_movie(id: int) -> dict:
    for movie in movies:
        if int(movie["id"]) == id:
            movies.remove(movie)
            return {
                "data": f"Movie with id {id} has been removed."
            }

    return {
        "data": f"Movie with id {id} not found."
    }