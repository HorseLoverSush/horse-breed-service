from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import init_database
from app.core.error_handlers import EXCEPTION_HANDLERS
from app.core.middleware import RequestTrackingMiddleware, SecurityMiddleware, RateLimitingMiddleware
from app.core.enhanced_logging import setup_enhanced_logging, get_logger, LoggingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import init_database
from app.core.error_handlers import EXCEPTION_HANDLERS
from app.core.middleware import RequestTrackingMiddleware, SecurityMiddleware, RateLimitingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_enhanced_logging()
    logger = get_logger("main")
    logger.info("Starting up Horse Breed Service application...")
    
    init_database()
    logger.info("Database initialization completed.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Horse Breed Service application...")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        description="A microservice for managing horse breed information",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Add exception handlers (must be added before middleware)
    for exception_type, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_type, handler)
    
    # Add custom middleware (order matters - last added is first to process requests)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitingMiddleware, calls=100, period=60)  # 100 requests per minute
    app.add_middleware(LoggingMiddleware)  # Enhanced logging with correlation IDs
    app.add_middleware(RequestTrackingMiddleware)
    
    # Add CORS middleware (should be last middleware to be added)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION
        }
    
    return app


# Create the FastAPI app instance
app = create_application()