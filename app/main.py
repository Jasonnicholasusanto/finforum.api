from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from core.db import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # SQLModel.metadata.drop_all(engine)

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Welcome to Equitalks API."}
