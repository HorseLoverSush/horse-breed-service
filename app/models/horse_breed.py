from typing import List, Optional
from app.schemas.horse_breed import TemperamentType


class HorseBreedModel:
    """In-memory horse breed model for demonstration purposes"""
    
    def __init__(
        self,
        id: int,
        name: str,
        origin: str,
        height_min: float,
        height_max: float,
        weight_min: int,
        weight_max: int,
        temperament: TemperamentType,
        colors: List[str],
        description: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.origin = origin
        self.height_min = height_min
        self.height_max = height_max
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.temperament = temperament
        self.colors = colors
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "origin": self.origin,
            "height_min": self.height_min,
            "height_max": self.height_max,
            "weight_min": self.weight_min,
            "weight_max": self.weight_max,
            "temperament": self.temperament,
            "colors": self.colors,
            "description": self.description
        }