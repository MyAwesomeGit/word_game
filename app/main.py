from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from api.routes import router
from api.exception_handlers import register_exception_handlers
from core.logging_config import LoggingConfigurator

# Configure logging
log_configurator = LoggingConfigurator()
logger = log_configurator.configure()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("=" * 60)
    logger.info("WORD GAME API STARTED")
    logger.info(f"Server time: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("WORD GAME API SHUTTING DOWN")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(title="Word Game API", lifespan=lifespan)

# Register exception handlers
register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
