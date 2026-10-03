from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

client: AsyncIOMotorClient = None


async def connect_to_mongo() -> None:
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    await db.games.create_index("title", unique=True)


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()


def get_db() -> AsyncIOMotorDatabase:
    return client[settings.MONGODB_DB_NAME]