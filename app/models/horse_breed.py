from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class HorseBreed(Base):
    """
    Horse Breed model representing a horse breed in the database.
    """
    __tablename__ = "horse_breeds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    origin_country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    average_height = Column(String(50), nullable=True)  # e.g., "15-16 hands"
    average_weight = Column(String(50), nullable=True)  # e.g., "1000-1200 lbs"
    temperament = Column(String(200), nullable=True)
    primary_use = Column(String(100), nullable=True)  # e.g., "Racing", "Show", "Work"
    is_active = Column(Boolean, default=True, nullable=False)
    food_requirements = Column(Text, nullable=True)  # e.g., "Grass, Hay, Grains"
    exercise_needs = Column(Text, nullable=True)  # e.g., "Daily riding, turnout"
    common_health_issues = Column(Text, nullable=True)  # e.g., "Col
    habitat_requirements = Column(Text, nullable=True)  # e.g., "Shelter, pasture"
    grooming_needs = Column(Text, nullable=True)  # e.g., "Regular brushing
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<HorseBreed(id={self.id}, name='{self.name}')>"