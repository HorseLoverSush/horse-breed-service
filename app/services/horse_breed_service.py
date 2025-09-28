from typing import List, Optional
from app.models.horse_breed import HorseBreedModel
from app.schemas.horse_breed import HorseBreedCreate, HorseBreedUpdate, TemperamentType


class HorseBreedService:
    """Service class for managing horse breeds (in-memory storage for demo)"""
    
    def __init__(self):
        self._breeds: List[HorseBreedModel] = []
        self._next_id = 1
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with some sample horse breeds"""
        sample_breeds = [
            {
                "name": "Arabian",
                "origin": "Arabian Peninsula",
                "height_min": 14.1,
                "height_max": 15.1,
                "weight_min": 800,
                "weight_max": 1000,
                "temperament": TemperamentType.SPIRITED,
                "colors": ["chestnut", "bay", "black", "gray"],
                "description": "Known for their distinctive head shape and high tail carriage"
            },
            {
                "name": "Thoroughbred",
                "origin": "England",
                "height_min": 15.0,
                "height_max": 17.0,
                "weight_min": 1000,
                "weight_max": 1200,
                "temperament": TemperamentType.ENERGETIC,
                "colors": ["bay", "chestnut", "brown", "black", "gray"],
                "description": "Bred for racing, known for speed and agility"
            },
            {
                "name": "Clydesdale",
                "origin": "Scotland",
                "height_min": 16.0,
                "height_max": 18.0,
                "weight_min": 1800,
                "weight_max": 2200,
                "temperament": TemperamentType.GENTLE,
                "colors": ["bay", "brown", "black", "chestnut"],
                "description": "Large draft horse known for strength and distinctive feathered feet"
            }
        ]
        
        for breed_data in sample_breeds:
            breed = HorseBreedModel(id=self._next_id, **breed_data)
            self._breeds.append(breed)
            self._next_id += 1
    
    def get_all_breeds(self) -> List[HorseBreedModel]:
        """Get all horse breeds"""
        return self._breeds.copy()
    
    def get_breed_by_id(self, breed_id: int) -> Optional[HorseBreedModel]:
        """Get a horse breed by ID"""
        for breed in self._breeds:
            if breed.id == breed_id:
                return breed
        return None
    
    def create_breed(self, breed_data: HorseBreedCreate) -> HorseBreedModel:
        """Create a new horse breed"""
        breed = HorseBreedModel(
            id=self._next_id,
            name=breed_data.name,
            origin=breed_data.origin,
            height_min=breed_data.height_min,
            height_max=breed_data.height_max,
            weight_min=breed_data.weight_min,
            weight_max=breed_data.weight_max,
            temperament=breed_data.temperament,
            colors=breed_data.colors,
            description=breed_data.description
        )
        self._breeds.append(breed)
        self._next_id += 1
        return breed
    
    def update_breed(self, breed_id: int, breed_data: HorseBreedUpdate) -> Optional[HorseBreedModel]:
        """Update an existing horse breed"""
        breed = self.get_breed_by_id(breed_id)
        if not breed:
            return None
        
        # Update only provided fields
        update_data = breed_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(breed, field, value)
        
        return breed
    
    def delete_breed(self, breed_id: int) -> bool:
        """Delete a horse breed"""
        for i, breed in enumerate(self._breeds):
            if breed.id == breed_id:
                del self._breeds[i]
                return True
        return False
    
    def search_breeds_by_name(self, name: str) -> List[HorseBreedModel]:
        """Search horse breeds by name (case-insensitive partial match)"""
        name_lower = name.lower()
        return [breed for breed in self._breeds if name_lower in breed.name.lower()]


# Global service instance
horse_breed_service = HorseBreedService()