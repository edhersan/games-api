from fastapi import FastAPI
from app.database import get_db, ensure_indexes, close_mongo_connection
from app.routers import games

app = FastAPI(
    title="Games API",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup():
    await ensure_indexes()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


app.include_router(games.router)


@app.get("/health")
async def health():
    return {"status": "ok"}