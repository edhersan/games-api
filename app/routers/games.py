import re
from fastapi import APIRouter, Depends, HTTPException, Path
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.database import get_db
from app.schemas.game import (
    GameResponse,
    GameArtResponse,
    GameInfoResponse,
)

router = APIRouter(prefix="/games", tags=["games"])


def serialize_game(game: dict) -> dict:
    """Convierte ObjectId a string en el documento"""
    if game and "_id" in game:
        game["_id"] = str(game["_id"])
    return game


def build_title_query(identifier: str) -> dict:
    """Construye query case-insensitive escapando caracteres especiales de regex"""
    escaped = re.escape(identifier.strip())
    return {"title": {"$regex": f"^{escaped}$", "$options": "i"}}


async def get_db_safe() -> AsyncIOMotorDatabase:
    """Wrapper que convierte errores de conexión en HTTP 503"""
    try:
        return await get_db()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


async def find_game_by_id_or_title(
    identifier: str = Path(..., description="ID (ObjectId) o nombre del juego"),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
) -> dict:
    """
    Busca un juego por ObjectId o por título (case-insensitive).
    Retorna el documento completo del juego.
    """
    try:
        if ObjectId.is_valid(identifier):
            query = {"_id": ObjectId(identifier)}
        else:
            query = build_title_query(identifier)
        
        game = await db.games.find_one(query)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return serialize_game(game)
    except HTTPException:
        raise
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def find_game_by_id_or_title_projection(
    identifier: str,
    projection: dict,
    db: AsyncIOMotorDatabase
) -> dict:
    """Busca un juego por ObjectId o título con proyección específica"""
    try:
        if ObjectId.is_valid(identifier):
            query = {"_id": ObjectId(identifier)}
        else:
            query = build_title_query(identifier)
        
        game = await db.games.find_one(query, projection)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return serialize_game(game)
    except HTTPException:
        raise
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{identifier}",
    response_model=GameResponse,
    summary="Obtener juego completo",
    description="Obtiene toda la información disponible de un juego por ID o nombre"
)
async def get_game_full(
    game: dict = Depends(find_game_by_id_or_title)
):
    return game


@router.get(
    "/{identifier}/art",
    response_model=GameArtResponse,
    summary="Obtener arte del juego",
    description="Obtiene la información visual del juego (thumbnail, capturas) por ID o nombre"
)
async def get_game_art(
    identifier: str = Path(..., description="ID (ObjectId) o nombre del juego"),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    game = await find_game_by_id_or_title_projection(
        identifier,
        {"_id": 1, "title": 1, "thumbnail": 1, "screenshots": 1},
        db
    )
    return game


@router.get(
    "/{identifier}/info",
    response_model=GameInfoResponse,
    summary="Obtener info y descripción del juego",
    description="Obtiene la información descriptiva del juego por ID o nombre"
)
async def get_game_info(
    identifier: str = Path(..., description="ID (ObjectId) o nombre del juego"),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    game = await find_game_by_id_or_title_projection(
        identifier,
        {"_id": 1, "title": 1, "short_description": 1, "description": 1, 
         "publisher": 1, "developer": 1, "genre": 1, "platform": 1, 
         "release_date": 1, "game_url": 1, "minimum_system_requirements": 1},
        db
    )
    return game