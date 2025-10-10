# services/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv

from .config.database import connect_to_mongo, close_mongo_connection
from .routes.auth import router as auth_router
from .routes.health import router as health_router
from .routes.agents import router as agent_router
from .routes.jobs import router as jobs_router
from .routes.candidates import router as candidates_router
from .routes.matches import router as matches_router
from .routes.analytics import router as analytics_router
# Scraping now handled by unified orchestrator
# Individual service routes removed - handled by unified orchestrator
from .routes.workflows import router as workflows_router
# from .services.agent_scheduler import start_scheduler, stop_scheduler
from .middleware.error_handler import add_exception_handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Make database connection non-blocking for faster startup
    logger.info("🚀 Starting FastAPI application...")

    # Start database connection in background (non-blocking)
    import asyncio
    async def connect_db():
        try:
            await connect_to_mongo()
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
            logger.warning("⚠️ Continuing without database - some features may be limited")

    # Don't wait for database connection - let it happen in background
    asyncio.create_task(connect_db())
    logger.info("🔄 Database connection started in background")

    # start_scheduler()
    yield
    # Shutdown
    # stop_scheduler()
    try:
        await close_mongo_connection()
    except Exception as e:
        logger.warning(f"⚠️ Error closing database connection: {e}")

app = FastAPI(
    title="AI Recruitment Agent API",
    description="Autonomous recruitment platform with AI-powered job discovery and candidate matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(agent_router, prefix="/api", tags=["agents"])
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])
app.include_router(candidates_router, prefix="/api/v1", tags=["candidates"])
app.include_router(matches_router, prefix="/api/v1", tags=["matches"])
app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
# Scraping handled by unified orchestrator
# Individual service routes removed - handled by unified orchestrator
app.include_router(workflows_router, prefix="/api/v1/workflows", tags=["workflows"])

@app.get("/")
def read_root():
    """Root endpoint for quick health check"""
    return {
        "message": "AI Recruitment Services are running",
        "status": "healthy",
        "service": "AI Recruitment Agent API",
        "version": "1.0.0"
    }

@app.get("/ping")
def ping():
    """Ultra-fast ping endpoint for Render health checks"""
    return {"status": "ok", "timestamp": "2025-09-18"}

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for deployment platforms like Render
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
