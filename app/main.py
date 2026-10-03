from fastapi import FastAPI
from app.routers import games

app = FastAPI(
    title="Games API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(games.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}