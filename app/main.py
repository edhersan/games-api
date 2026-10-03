from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import games


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Games API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.include_router(games.router)


@app.get("/health")
async def health():
    return {"status": "ok"}