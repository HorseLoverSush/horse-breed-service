from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.horse_breed import HorseBreed
from app.schemas.horse_breed import HorseBreedCreate, HorseBreedUpdate


class HorseBreedService:
    """
    Service class for horse breed operations.
    Contains business logic for CRUD operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_breeds(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        active_only: bool = True
    ) -> tuple[List[HorseBreed], int]:
        """
        Get list of horse breeds with pagination and optional search.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term to filter by name or origin country
            active_only: Whether to return only active breeds
            
        Returns:
            Tuple of (breeds_list, total_count)
        """
        query = self.db.query(HorseBreed)
        
        # Filter by active status if requested
        if active_only:
            query = query.filter(HorseBreed.is_active == True)
        
        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (HorseBreed.name.ilike(search_filter)) |
                (HorseBreed.origin_country.ilike(search_filter))
            )
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and get results
        breeds = query.offset(skip).limit(limit).all()
        
        return breeds, total
    
    def get_breed_by_id(self, breed_id: int) -> Optional[HorseBreed]:
        """
        Get a horse breed by its ID.
        
        Args:
            breed_id: The ID of the breed to retrieve
            
        Returns:
            HorseBreed object or None if not found
        """
        return self.db.query(HorseBreed).filter(HorseBreed.id == breed_id).first()
    
    def get_breed_by_name(self, name: str) -> Optional[HorseBreed]:
        """
        Get a horse breed by its name.
        
        Args:
            name: The name of the breed to retrieve
            
        Returns:
            HorseBreed object or None if not found
        """
        return self.db.query(HorseBreed).filter(HorseBreed.name == name).first()
    
    def create_breed(self, breed_data: HorseBreedCreate) -> HorseBreed:
        """
        Create a new horse breed.
        
        Args:
            breed_data: The breed data to create
            
        Returns:
            Created HorseBreed object
            
        Raises:
            ValueError: If breed with same name already exists
        """
        # Check if breed with same name already exists
        existing_breed = self.get_breed_by_name(breed_data.name)
        if existing_breed:
            raise ValueError(f"Horse breed with name '{breed_data.name}' already exists")
        
        # Create new breed
        db_breed = HorseBreed(**breed_data.dict())
        self.db.add(db_breed)
        self.db.commit()
        self.db.refresh(db_breed)
        
        return db_breed
    
    def update_breed(self, breed_id: int, breed_data: HorseBreedUpdate) -> Optional[HorseBreed]:
        """
        Update an existing horse breed.
        
        Args:
            breed_id: The ID of the breed to update
            breed_data: The updated breed data
            
        Returns:
            Updated HorseBreed object or None if not found
            
        Raises:
            ValueError: If trying to update name to an existing breed name
        """
        # Get existing breed
        db_breed = self.get_breed_by_id(breed_id)
        if not db_breed:
            return None
        
        # Check if name is being updated and if it conflicts with existing breed
        if breed_data.name and breed_data.name != db_breed.name:
            existing_breed = self.get_breed_by_name(breed_data.name)
            if existing_breed:
                raise ValueError(f"Horse breed with name '{breed_data.name}' already exists")
        
        # Update breed with provided data
        update_data = breed_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_breed, field, value)
        
        self.db.commit()
        self.db.refresh(db_breed)
        
        return db_breed
    
    def delete_breed(self, breed_id: int) -> bool:
        """
        Soft delete a horse breed by setting is_active to False.
        
        Args:
            breed_id: The ID of the breed to delete
            
        Returns:
            True if breed was deleted, False if not found
        """
        db_breed = self.get_breed_by_id(breed_id)
        if not db_breed:
            return False
        
        db_breed.is_active = False
        self.db.commit()
        
        return True