from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.horse_breed import HorseBreed, HorseBreedCreate, HorseBreedUpdate
from app.services.horse_breed_service import horse_breed_service

router = APIRouter(prefix="/horse-breeds", tags=["horse-breeds"])


@router.get("/", response_model=List[HorseBreed], summary="Get all horse breeds")
async def get_all_horse_breeds():
    """
    Retrieve all horse breeds in the system.
    
    Returns:
        List of all horse breeds with their details
    """
    breeds = horse_breed_service.get_all_breeds()
    return [breed.to_dict() for breed in breeds]


@router.get("/search", response_model=List[HorseBreed], summary="Search horse breeds by name")
async def search_horse_breeds(
    name: str = Query(..., description="Name to search for (partial match, case-insensitive)")
):
    """
    Search for horse breeds by name.
    
    Args:
        name: Partial name to search for (case-insensitive)
    
    Returns:
        List of horse breeds matching the search criteria
    """
    breeds = horse_breed_service.search_breeds_by_name(name)
    return [breed.to_dict() for breed in breeds]


@router.get("/{breed_id}", response_model=HorseBreed, summary="Get horse breed by ID")
async def get_horse_breed(breed_id: int):
    """
    Retrieve a specific horse breed by its ID.
    
    Args:
        breed_id: Unique identifier of the horse breed
    
    Returns:
        Horse breed details
    
    Raises:
        HTTPException: 404 if breed not found
    """
    breed = horse_breed_service.get_breed_by_id(breed_id)
    if not breed:
        raise HTTPException(status_code=404, detail="Horse breed not found")
    return breed.to_dict()


@router.post("/", response_model=HorseBreed, status_code=201, summary="Create a new horse breed")
async def create_horse_breed(breed_data: HorseBreedCreate):
    """
    Create a new horse breed.
    
    Args:
        breed_data: Horse breed information
    
    Returns:
        Created horse breed with assigned ID
    """
    breed = horse_breed_service.create_breed(breed_data)
    return breed.to_dict()


@router.put("/{breed_id}", response_model=HorseBreed, summary="Update horse breed")
async def update_horse_breed(breed_id: int, breed_data: HorseBreedUpdate):
    """
    Update an existing horse breed.
    
    Args:
        breed_id: Unique identifier of the horse breed
        breed_data: Updated horse breed information
    
    Returns:
        Updated horse breed details
    
    Raises:
        HTTPException: 404 if breed not found
    """
    breed = horse_breed_service.update_breed(breed_id, breed_data)
    if not breed:
        raise HTTPException(status_code=404, detail="Horse breed not found")
    return breed.to_dict()


@router.delete("/{breed_id}", status_code=204, summary="Delete horse breed")
async def delete_horse_breed(breed_id: int):
    """
    Delete a horse breed.
    
    Args:
        breed_id: Unique identifier of the horse breed
    
    Raises:
        HTTPException: 404 if breed not found
    """
    success = horse_breed_service.delete_breed(breed_id)
    if not success:
        raise HTTPException(status_code=404, detail="Horse breed not found")