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
            tlsAllowInvalidCertificates=True,  # For Vercel SSL issues
        )
    return _client


async def get_db() -> AsyncIOMotorDatabase:
    client = get_mongo_client()
    db = client[settings.MONGODB_DB_NAME]
    # Test connection on each request
    try:
        await db.command("ping")
    except Exception as e:
        # Close and reset client to force reconnection
        global _client
        if _client:
            _client.close()
            _client = None
        raise RuntimeError(f"Database connection failed: {e}")
    return db


async def close_mongo_connection():
    global _client
    if _client:
        _client.close()
        _client = None