from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import os

_client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=0,
        )
    return _client


async def get_db() -> AsyncIOMotorDatabase:
    client = get_mongo_client()
    db = client[settings.MONGODB_DB_NAME]
    try:
        await db.command("ping")
    except Exception:
        client.close()
        _client = None
        client = get_mongo_client()
        db = client[settings.MONGODB_DB_NAME]
    return db


async def ensure_indexes():
    db = await get_db()
    await db.games.create_index("title", unique=True)


async def close_mongo_connection():
    global _client
    if _client:
        _client.close()
        _client = None