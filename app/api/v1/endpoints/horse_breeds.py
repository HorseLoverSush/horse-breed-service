from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.horse_breed import (
    HorseBreedCreate, 
    HorseBreedUpdate, 
    HorseBreedResponse, 
    HorseBreedListResponse
)
from app.services.horse_breed_service import HorseBreedService
from app.core.exceptions import NotFoundError
from math import ceil

# Create router for horse breeds endpoints
router = APIRouter()


@router.get("/", response_model=HorseBreedListResponse)
async def get_breeds(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or origin country"),
    active_only: bool = Query(True, description="Return only active breeds"),
    db: Session = Depends(get_db)
):
    """
    Get list of horse breeds with pagination and optional search.
    """
    service = HorseBreedService(db)
    skip = (page - 1) * size
    
    breeds, total = service.get_breeds(
        skip=skip, 
        limit=size, 
        search=search, 
        active_only=active_only
    )
    
    pages = ceil(total / size) if total > 0 else 1
    
    return HorseBreedListResponse(
        breeds=breeds,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{breed_id}", response_model=HorseBreedResponse)
async def get_breed(
    breed_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific horse breed by ID.
    """
    service = HorseBreedService(db)
    breed = service.get_breed_by_id(breed_id)
    
    if not breed:
        raise NotFoundError(resource="Horse breed", identifier=breed_id)
    
    return breed


@router.post("/", response_model=HorseBreedResponse, status_code=201)
async def create_breed(
    breed_data: HorseBreedCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new horse breed.
    """
    service = HorseBreedService(db)
    breed = service.create_breed(breed_data)
    return breed


@router.put("/{breed_id}", response_model=HorseBreedResponse)
async def update_breed(
    breed_id: int,
    breed_data: HorseBreedUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing horse breed.
    """
    service = HorseBreedService(db)
    breed = service.update_breed(breed_id, breed_data)
    return breed


@router.delete("/{breed_id}", status_code=204)
async def delete_breed(
    breed_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a horse breed (sets is_active to False).
    """
    service = HorseBreedService(db)
    service.delete_breed(breed_id)
    return None