from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.schemas.game import (
    GameCreate,
    GameUpdate,
    GameResponse,
    GameArtResponse,
    GameInfoResponse,
    GameFullResponse,
)

router = APIRouter(prefix="/games", tags=["games"])


def validate_object_id(game_id: str = Path(..., description="ID del juego (ObjectId)")) -> str:
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    return game_id


def to_object_id(game_id: str) -> ObjectId:
    return ObjectId(game_id)


def serialize_game(game: dict) -> dict:
    """Convierte ObjectId a string en el documento"""
    if game and "_id" in game:
        game["_id"] = str(game["_id"])
    return game


async def get_db_safe() -> AsyncIOMotorDatabase:
    """Wrapper que convierte errores de conexión en HTTP 503"""
    try:
        return await get_db()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")



@router.get(
    "/{game_id}",
    response_model=GameFullResponse,
    summary="Obtener juego completo",
    description="Obtiene toda la información disponible de un juego (básico, arte, info y full_info)"
)
async def get_game_full(
    game_id: str = Depends(validate_object_id),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        game = await db.games.find_one({"_id": to_object_id(game_id)})
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return serialize_game(game)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{game_id}/art",
    response_model=GameArtResponse,
    summary="Obtener arte del juego",
    description="Obtiene solo la información visual del juego (portada, capturas, banner, icono)"
)
async def get_game_art(
    game_id: str = Depends(validate_object_id),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        game = await db.games.find_one(
            {"_id": to_object_id(game_id)},
            {"_id": 1, "title": 1, "art": 1}
        )
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return serialize_game(game)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{game_id}/info",
    response_model=GameInfoResponse,
    summary="Obtener info y descripción del juego",
    description="Obtiene la información descriptiva del juego (descripción, desarrollador, publisher, ratings, etc.)"
)
async def get_game_info(
    game_id: str = Depends(validate_object_id),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        game = await db.games.find_one(
            {"_id": to_object_id(game_id)},
            {"_id": 1, "title": 1, "info": 1}
        )
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return serialize_game(game)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
