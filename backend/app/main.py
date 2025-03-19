import logging
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from typing import Dict

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.errors import add_exception_handlers
from app.db.connections import mongodb, redis_conn, pinecone_conn
from app.schemas import StandardResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a unique ID for API routes to improve Swagger documentation."""
    if route.tags and len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    else:
        return f"root-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend Template",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Add exception handlers
add_exception_handlers(app)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the API router with version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_model=StandardResponse[dict])
async def root():
    """Root endpoint providing basic API information."""
    return StandardResponse(
        data={"message": "Welcome to the FastAPI Backend Template"},
        message="API is running"
    )

@app.get("/health", response_model=StandardResponse[Dict[str, str]])
async def health_check():
    """Enhanced health check endpoint that tests all database connections."""
    health_status = {}
    all_healthy = True

    # Check MongoDB
    mongodb_status = await check_mongodb()
    health_status["mongodb"] = "healthy" if mongodb_status["connected"] else "unhealthy"
    all_healthy = all_healthy and mongodb_status["connected"]

    # Check Redis
    redis_status = await check_redis()
    health_status["redis"] = "healthy" if redis_status["connected"] else "unhealthy"
    all_healthy = all_healthy and redis_status["connected"]

    # Check Pinecone if configured
    if settings.PINECONE_API_KEY:
        pinecone_status = check_pinecone()
        health_status["pinecone"] = "healthy" if pinecone_status["connected"] else "unhealthy"
        all_healthy = all_healthy and pinecone_status["connected"]
    else:
        health_status["pinecone"] = "not_configured"

    # Add overall API status
    health_status["status"] = "healthy" if all_healthy else "unhealthy"
    
    return StandardResponse(
        data=health_status,
        message="All systems operational" if all_healthy else "Some systems are degraded",
        success=all_healthy
    )

async def check_mongodb() -> Dict[str, bool]:
    """Test MongoDB connection."""
    try:
        await mongodb.client.admin.command('ping')
        return {"connected": True}
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {"connected": False, "error": str(e)}

async def check_redis() -> Dict[str, bool]:
    """Test Redis connection."""
    try:
        await redis_conn.client.ping()
        return {"connected": True}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"connected": False, "error": str(e)}

def check_pinecone() -> Dict[str, bool]:
    """Test Pinecone connection."""
    try:
        # Pinecone doesn't have a ping method, so we'll check if the index is initialized
        if pinecone_conn._index is not None:
            # Try to fetch index stats as a connection test
            pinecone_conn.index.describe_index_stats()
            return {"connected": True}
        return {"connected": False, "error": "Index not initialized"}
    except Exception as e:
        logger.error(f"Pinecone health check failed: {e}")
        return {"connected": False, "error": str(e)}

@app.on_event("startup")
async def startup_db_client() -> None:
    """Initialize database connections on application startup."""
    try:
        # Initialize MongoDB (async)
        logger.info("Connecting to MongoDB...")
        await mongodb.connect()
        logger.info("Successfully connected to MongoDB")

        # Initialize Redis (async)
        logger.info("Connecting to Redis...")
        await redis_conn.connect()
        logger.info("Successfully connected to Redis")

        # Initialize Pinecone (sync) - optional
        if settings.PINECONE_API_KEY:
            logger.info("Connecting to Pinecone...")
            try:
                pinecone_conn.connect()
                logger.info("Successfully connected to Pinecone")
            except Exception as e:
                logger.warning(f"Failed to connect to Pinecone: {e}")
        else:
            logger.warning("Skipping Pinecone connection - API key not provided")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Re-raise the exception to prevent the application from starting with failed connections
        raise


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    """Close database connections on application shutdown."""
    try:
        # Close connections in reverse order of initialization
        
        # Close Pinecone (sync) - if it was initialized
        if settings.PINECONE_API_KEY:
            logger.info("Closing Pinecone connection...")
            pinecone_conn.close()
            logger.info("Pinecone connection closed")

        # Close Redis (async)
        logger.info("Closing Redis connection...")
        await redis_conn.close()
        logger.info("Redis connection closed")

        # Close MongoDB (async)
        logger.info("Closing MongoDB connection...")
        await mongodb.close()
        logger.info("MongoDB connection closed")

    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")
        # Don't re-raise the exception during shutdown to ensure all cleanup attempts are made
