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
    "",
    response_model=list[GameResponse],
    summary="Listar juegos",
    description="Obtiene una lista paginada de todos los juegos"
)
async def list_games(
    skip: int = Query(0, ge=0, description="Número de juegos a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de juegos por página"),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        cursor = db.games.find().skip(skip).limit(limit)
        games = await cursor.to_list(length=limit)
        return [serialize_game(g) for g in games]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@router.post(
    "",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear juego",
    description="Crea un nuevo juego con toda su información (básico, arte, info, full_info)"
)
async def create_game(
    game: GameCreate,
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        doc = game.model_dump(exclude_none=True)
        result = await db.games.insert_one(doc)
        created = await db.games.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="Error al crear el juego")
        return serialize_game(created)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/{game_id}",
    response_model=GameResponse,
    summary="Actualizar juego",
    description="Actualiza parcialmente un juego (cualquier campo)"
)
async def update_game(
    game_update: GameUpdate,
    game_id: str = Depends(validate_object_id),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        existing = await db.games.find_one({"_id": to_object_id(game_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Juego no encontrado")

        update_data = game_update.model_dump(exclude_none=True, exclude_unset=True)
        if update_data:
            await db.games.update_one({"_id": to_object_id(game_id)}, {"$set": update_data})

        updated = await db.games.find_one({"_id": to_object_id(game_id)})
        return serialize_game(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar juego",
    description="Elimina un juego por su ID"
)
async def delete_game(
    game_id: str = Depends(validate_object_id),
    db: AsyncIOMotorDatabase = Depends(get_db_safe)
):
    try:
        result = await db.games.delete_one({"_id": to_object_id(game_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))