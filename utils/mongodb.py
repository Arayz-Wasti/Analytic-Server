from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.utils.settings import get_settings
import logging
from typing import Optional
from fastapi import status, HTTPException

log = logging.getLogger("analytic_server.db")
settings = get_settings()

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection and store client & database globally.
    Raises RuntimeError if connection fails.
    """
    global _client, _db
    if _client is not None and _db is not None:
        log.info("MongoDB connection already exists")
        return

    try:
        log.info("Connecting to MongoDB...")
        _client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,  # 5 seconds
            tz_aware=True
        )
        _db = _client[settings.DB_NAME]
        await _db.command("ping")
        log.info("MongoDB CONNECTED", extra={"db": settings.DB_NAME})
    except Exception as e:
        log.exception("Failed to connect to MongoDB")
        raise RuntimeError(f"Cannot connect to MongoDB: {e}")


async def close_mongo() -> None:
    """
    Gracefully close the MongoDB client.
    """
    global _client
    if _client:
        log.info("Closing MongoDB connection")
        _client.close()
        _client = None
    else:
        log.info("MongoDB client already closed")


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not initialized"
        )
    return _db
