"""Database connection utilities for MongoDB, Redis, and Pinecone.

This module provides connection utilities for the hybrid database architecture used in the
Political Social Media Analysis Platform. It implements connection management for:
- MongoDB: For storing social media content and engagement data
- Redis: For caching and real-time operations
- Pinecone: For vector similarity search and semantic analysis
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from functools import lru_cache

import motor.motor_asyncio
import pinecone
import redis.asyncio as redis
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from app.core.config import settings


class MongoDBConnection:
    """MongoDB connection manager using motor for async operations."""
    
    def __init__(self) -> None:
        """Initialize MongoDB connection manager."""
        self._client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self._db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Connect to MongoDB and initialize database."""
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test the connection
            await self._client.admin.command('ping')
            self._db = self._client[settings.MONGODB_DB]
            
            # Create indexes for common queries
            await self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    async def _create_indexes(self) -> None:
        """Create indexes for common queries."""
        if not self._db:
            return

        # Posts collection indexes
        await self._db.posts.create_index([("created_at", -1)])
        await self._db.posts.create_index([("platform", 1), ("external_id", 1)], unique=True)
        await self._db.posts.create_index([("content", "text")])
        
        # Comments collection indexes
        await self._db.comments.create_index([("post_id", 1), ("created_at", -1)])
        await self._db.comments.create_index([("content", "text")])

    @property
    def db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get the database instance."""
        if not self._db:
            raise ConnectionError("MongoDB connection not initialized")
        return self._db

    @property
    def client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Get the client instance."""
        if not self._client:
            raise ConnectionError("MongoDB client not initialized")
        return self._client

    async def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None


class RedisConnection:
    """Redis connection manager for async operations."""
    
    def __init__(self) -> None:
        """Initialize Redis connection manager."""
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self._client = redis.from_url(
                settings.REDIS_URI,
                encoding="utf-8",
                decode_responses=True
            )
            # Test the connection
            await self._client.ping()
        except RedisConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    @property
    def client(self) -> redis.Redis:
        """Get the Redis client instance."""
        if not self._client:
            raise ConnectionError("Redis connection not initialized")
        return self._client

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


class PineconeConnection:
    """Pinecone connection manager for vector similarity search."""
    
    def __init__(self) -> None:
        """Initialize Pinecone connection manager."""
        self._index = None

    def connect(self) -> None:
        """Initialize Pinecone connection and ensure index exists."""
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            # Create index if it doesn't exist
            if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=384,  # Dimension for all-MiniLM-L6-v2 embeddings
                    metric="cosine"
                )
            
            self._index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Pinecone: {e}")

    @property
    def index(self) -> pinecone.Index:
        """Get the Pinecone index instance."""
        if not self._index:
            raise ConnectionError("Pinecone connection not initialized")
        return self._index

    def close(self) -> None:
        """Clean up Pinecone resources."""
        if self._index:
            self._index = None
            pinecone.deinit()


# Singleton instances
mongodb = MongoDBConnection()
redis_conn = RedisConnection()
pinecone_conn = PineconeConnection()


@asynccontextmanager
async def get_mongodb() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """Async context manager for getting MongoDB database instance."""
    if not mongodb._client:
        await mongodb.connect()
    try:
        yield mongodb.db
    except Exception as e:
        raise ConnectionError(f"Error accessing MongoDB: {e}")


@asynccontextmanager
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Async context manager for getting Redis client instance."""
    if not redis_conn._client:
        await redis_conn.connect()
    try:
        yield redis_conn.client
    except RedisError as e:
        raise ConnectionError(f"Error accessing Redis: {e}")


@lru_cache()
def get_pinecone() -> pinecone.Index:
    """Get Pinecone index instance with caching."""
    if not pinecone_conn._index:
        pinecone_conn.connect()
    return pinecone_conn.index


async def close_db_connections() -> None:
    """Close all database connections."""
    await mongodb.close()
    await redis_conn.close()
    pinecone_conn.close() 