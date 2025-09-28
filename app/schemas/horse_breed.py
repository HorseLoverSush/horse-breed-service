from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HorseBreedBase(BaseModel):
    """
    Base schema for Horse Breed with common fields.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Name of the horse breed")
    origin_country: Optional[str] = Field(None, max_length=100, description="Country of origin")
    description: Optional[str] = Field(None, description="Description of the breed")
    average_height: Optional[str] = Field(None, max_length=50, description="Average height (e.g., '15-16 hands')")
    average_weight: Optional[str] = Field(None, max_length=50, description="Average weight (e.g., '1000-1200 lbs')")
    temperament: Optional[str] = Field(None, max_length=200, description="Breed temperament")
    primary_use: Optional[str] = Field(None, max_length=100, description="Primary use (e.g., 'Racing', 'Show', 'Work')")


class HorseBreedCreate(HorseBreedBase):
    """
    Schema for creating a new horse breed.
    """
    pass


class HorseBreedUpdate(BaseModel):
    """
    Schema for updating an existing horse breed.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the horse breed")
    origin_country: Optional[str] = Field(None, max_length=100, description="Country of origin")
    description: Optional[str] = Field(None, description="Description of the breed")
    average_height: Optional[str] = Field(None, max_length=50, description="Average height")
    average_weight: Optional[str] = Field(None, max_length=50, description="Average weight")
    temperament: Optional[str] = Field(None, max_length=200, description="Breed temperament")
    primary_use: Optional[str] = Field(None, max_length=100, description="Primary use")
    is_active: Optional[bool] = Field(None, description="Whether the breed is active")


class HorseBreedResponse(HorseBreedBase):
    """
    Schema for horse breed response with all fields including database metadata.
    """
    id: int = Field(..., description="Unique identifier for the breed")
    is_active: bool = Field(..., description="Whether the breed is active")
    created_at: datetime = Field(..., description="When the breed was created")
    updated_at: Optional[datetime] = Field(None, description="When the breed was last updated")
    
    class Config:
        from_attributes = True


class HorseBreedListResponse(BaseModel):
    """
    Schema for paginated list of horse breeds.
    """
    breeds: list[HorseBreedResponse] = Field(..., description="List of horse breeds")
    total: int = Field(..., description="Total number of breeds")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")