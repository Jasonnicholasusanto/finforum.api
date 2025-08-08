import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from app.api.routes import user_profile
from app.core.db import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_db_and_tables()
        yield
    except asyncio.CancelledError:
        pass
    # SQLModel.metadata.drop_all(engine)


app = FastAPI(lifespan=lifespan)

app.include_router(user_profile.router)


@app.get("/")
async def root():
    return {"message": "Welcome to FinForum API."}
