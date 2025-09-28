from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TemperamentType(str, Enum):
    CALM = "calm"
    ENERGETIC = "energetic"
    SPIRITED = "spirited"
    GENTLE = "gentle"
    AGGRESSIVE = "aggressive"


class HorseBreedBase(BaseModel):
    name: str = Field(..., description="Name of the horse breed")
    origin: str = Field(..., description="Country or region of origin")
    height_min: float = Field(..., description="Minimum height in hands", ge=10.0, le=20.0)
    height_max: float = Field(..., description="Maximum height in hands", ge=10.0, le=20.0)
    weight_min: int = Field(..., description="Minimum weight in pounds", ge=500, le=3000)
    weight_max: int = Field(..., description="Maximum weight in pounds", ge=500, le=3000)
    temperament: TemperamentType = Field(..., description="General temperament of the breed")
    colors: List[str] = Field(default=[], description="Common colors for this breed")
    description: Optional[str] = Field(None, description="Description of the breed")


class HorseBreedCreate(HorseBreedBase):
    pass


class HorseBreedUpdate(BaseModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    height_min: Optional[float] = Field(None, ge=10.0, le=20.0)
    height_max: Optional[float] = Field(None, ge=10.0, le=20.0)
    weight_min: Optional[int] = Field(None, ge=500, le=3000)
    weight_max: Optional[int] = Field(None, ge=500, le=3000)
    temperament: Optional[TemperamentType] = None
    colors: Optional[List[str]] = None
    description: Optional[str] = None


class HorseBreed(HorseBreedBase):
    id: int = Field(..., description="Unique identifier for the horse breed")

    class Config:
        from_attributes = True