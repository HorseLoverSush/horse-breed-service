from fastapi import APIRouter
from app.api.v1.endpoints import horse_breeds

# Create API router for version 1
api_router = APIRouter()

# Include horse breeds endpoints
api_router.include_router(
    horse_breeds.router, 
    prefix="/breeds", 
    tags=["Horse Breeds"]
)