from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.horse_breeds import router as horse_breeds_router

# Create FastAPI application
app = FastAPI(
    title="Horse Breed Microservice",
    description="A microservice for managing horse breed information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(horse_breeds_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Welcome to the Horse Breed Microservice",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {"status": "healthy", "service": "horse-breed-microservice"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)