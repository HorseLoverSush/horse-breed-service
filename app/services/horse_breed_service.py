from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.models.horse_breed import HorseBreed
from app.schemas.horse_breed import HorseBreedCreate, HorseBreedUpdate
from app.core.exceptions import NotFoundError, ConflictError, DatabaseError
from app.core.enhanced_logging import get_logger, log_performance, log_business_event, LoggingContext


class HorseBreedService:
    """
    Service class for horse breed operations.
    Contains business logic for CRUD operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("service.horse_breed")
    
    @log_performance("get_breeds", threshold_ms=500.0)
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
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with LoggingContext("get_breeds_query", self.logger, skip=skip, limit=limit, search=search, active_only=active_only):
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
                    self.logger.info("Search filter applied", extra={"search_term": search})
                
                # Get total count for pagination
                total = query.count()
                
                # Apply pagination and get results
                breeds = query.offset(skip).limit(limit).all()
                
                self.logger.info(
                    "Breeds retrieved successfully",
                    extra={
                        "total_found": total,
                        "returned_count": len(breeds),
                        "has_search": search is not None,
                        "active_only": active_only
                    }
                )
                
                return breeds, total
            
        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to retrieve horse breeds",
                operation="get_breeds",
                details={"search": search, "skip": skip, "limit": limit, "error": str(e)}
            )
    
    def get_breed_by_id(self, breed_id: int) -> Optional[HorseBreed]:
        """
        Get a horse breed by its ID.
        
        Args:
            breed_id: The ID of the breed to retrieve
            
        Returns:
            HorseBreed object or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.db.query(HorseBreed).filter(HorseBreed.id == breed_id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(
                message=f"Failed to retrieve horse breed with ID {breed_id}",
                operation="get_breed_by_id",
                details={"breed_id": breed_id, "error": str(e)}
            )
    
    def get_breed_by_name(self, name: str) -> Optional[HorseBreed]:
        """
        Get a horse breed by its name.
        
        Args:
            name: The name of the breed to retrieve
            
        Returns:
            HorseBreed object or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return self.db.query(HorseBreed).filter(HorseBreed.name == name).first()
        except SQLAlchemyError as e:
            raise DatabaseError(
                message=f"Failed to retrieve horse breed with name '{name}'",
                operation="get_breed_by_name",
                details={"name": name, "error": str(e)}
            )
    
    @log_performance("create_breed", threshold_ms=1000.0, include_args=True)
    def create_breed(self, breed_data: HorseBreedCreate) -> HorseBreed:
        """
        Create a new horse breed.
        
        Args:
            breed_data: The breed data to create
            
        Returns:
            Created HorseBreed object
            
        Raises:
            ConflictError: If breed with same name already exists
            DatabaseError: If database operation fails
        """
        try:
            # Check if breed with same name already exists
            existing_breed = self.get_breed_by_name(breed_data.name)
            if existing_breed:
                raise ConflictError(
                    message=f"Horse breed with name '{breed_data.name}' already exists",
                    conflicting_field="name",
                    details={"existing_breed_id": existing_breed.id, "name": breed_data.name}
                )
            
            # Create new breed
            db_breed = HorseBreed(**breed_data.dict())
            self.db.add(db_breed)
            self.db.commit()
            self.db.refresh(db_breed)
            
            # Log business event
            log_business_event(
                self.logger,
                "horse_breed_created",
                {
                    "breed_id": db_breed.id,
                    "breed_name": db_breed.name,
                    "origin_country": db_breed.origin_country
                }
            )
            
            self.logger.info(
                "Horse breed created successfully",
                extra={
                    "breed_id": db_breed.id,
                    "breed_name": db_breed.name,
                    "created_at": db_breed.created_at.isoformat() if db_breed.created_at else None
                }
            )
            
            return db_breed
            
        except ConflictError:
            # Re-raise conflict errors as-is
            raise
        except SQLAlchemyError as e:
            # Rollback the transaction
            self.db.rollback()
            raise DatabaseError(
                message="Failed to create horse breed",
                operation="create_breed",
                details={"breed_name": breed_data.name, "error": str(e)}
            )
    
    @log_performance("update_breed", threshold_ms=1000.0, include_args=True)
    def update_breed(self, breed_id: int, breed_data: HorseBreedUpdate) -> HorseBreed:
        """
        Update an existing horse breed.
        
        Args:
            breed_id: The ID of the breed to update
            breed_data: The updated breed data
            
        Returns:
            Updated HorseBreed object
            
        Raises:
            NotFoundError: If breed with given ID is not found
            ConflictError: If trying to update name to an existing breed name
            DatabaseError: If database operation fails
        """
        try:
            # Get existing breed
            db_breed = self.get_breed_by_id(breed_id)
            if not db_breed:
                raise NotFoundError(
                    resource="Horse breed",
                    identifier=breed_id,
                    details={"operation": "update"}
                )
            
            # Check if name is being updated and if it conflicts with existing breed
            if breed_data.name and breed_data.name != db_breed.name:
                existing_breed = self.get_breed_by_name(breed_data.name)
                if existing_breed:
                    raise ConflictError(
                        message=f"Horse breed with name '{breed_data.name}' already exists",
                        conflicting_field="name",
                        details={
                            "existing_breed_id": existing_breed.id, 
                            "attempted_name": breed_data.name,
                            "current_breed_id": breed_id
                        }
                    )
            
            # Update breed with provided data
            update_data = breed_data.dict(exclude_unset=True)
            changed_fields = []
            
            for field, value in update_data.items():
                old_value = getattr(db_breed, field)
                if old_value != value:
                    changed_fields.append(field)
                setattr(db_breed, field, value)
            
            self.db.commit()
            self.db.refresh(db_breed)
            
            # Log business event
            log_business_event(
                self.logger,
                "horse_breed_updated",
                {
                    "breed_id": breed_id,
                    "breed_name": db_breed.name,
                    "changed_fields": changed_fields,
                    "update_count": len(changed_fields)
                }
            )
            
            self.logger.info(
                "Horse breed updated successfully",
                extra={
                    "breed_id": breed_id,
                    "breed_name": db_breed.name,
                    "changed_fields": changed_fields,
                    "updated_at": db_breed.updated_at.isoformat() if hasattr(db_breed, 'updated_at') and db_breed.updated_at else None
                }
            )
            
            return db_breed
            
        except (NotFoundError, ConflictError):
            # Re-raise our custom errors as-is
            raise
        except SQLAlchemyError as e:
            # Rollback the transaction
            self.db.rollback()
            raise DatabaseError(
                message=f"Failed to update horse breed with ID {breed_id}",
                operation="update_breed",
                details={"breed_id": breed_id, "error": str(e)}
            )
    
    @log_performance("delete_breed", threshold_ms=500.0)
    def delete_breed(self, breed_id: int) -> HorseBreed:
        """
        Soft delete a horse breed by setting is_active to False.
        
        Args:
            breed_id: The ID of the breed to delete
            
        Returns:
            The deleted (deactivated) HorseBreed object
            
        Raises:
            NotFoundError: If breed with given ID is not found
            DatabaseError: If database operation fails
        """
        try:
            db_breed = self.get_breed_by_id(breed_id)
            if not db_breed:
                raise NotFoundError(
                    resource="Horse breed",
                    identifier=breed_id,
                    details={"operation": "delete"}
                )
            
            db_breed.is_active = False
            self.db.commit()
            self.db.refresh(db_breed)
            
            # Log business event
            log_business_event(
                self.logger,
                "horse_breed_deleted",
                {
                    "breed_id": breed_id,
                    "breed_name": db_breed.name,
                    "deletion_type": "soft_delete"
                }
            )
            
            self.logger.info(
                "Horse breed soft deleted successfully",
                extra={
                    "breed_id": breed_id,
                    "breed_name": db_breed.name,
                    "is_active": db_breed.is_active
                }
            )
            
            return db_breed
            
        except NotFoundError:
            # Re-raise not found errors as-is
            raise
        except SQLAlchemyError as e:
            # Rollback the transaction
            self.db.rollback()
            raise DatabaseError(
                message=f"Failed to delete horse breed with ID {breed_id}",
                operation="delete_breed",
                details={"breed_id": breed_id, "error": str(e)}
            )