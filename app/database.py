from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

_client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        if not settings.MONGODB_URL:
            raise RuntimeError("MONGODB_URL not configured")
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
    return client[settings.MONGODB_DB_NAME]


async def close_mongo_connection():
    global _client
    if _client:
        _client.close()
        _client = None