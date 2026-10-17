from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import games

app = FastAPI(
    title="Games API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS para consumo desde navegador (la app móvil ignora estas cabeceras).
# El middleware también responde los preflight OPTIONS automáticamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

app.include_router(games.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}