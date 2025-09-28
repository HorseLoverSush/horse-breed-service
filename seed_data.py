# Sample Data Seeder
# This script adds sample horse breed data for testing the APIs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.horse_breed import HorseBreed
from datetime import datetime

def seed_data():
    """Add sample horse breed data to the database."""
    print("Adding sample horse breed data...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if data already exists
    existing_count = db.query(HorseBreed).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} horse breeds. Skipping seed.")
        db.close()
        return
    
    # Sample horse breeds data
    sample_breeds = [
        {
            "name": "Arabian",
            "origin_country": "Arabian Peninsula",
            "description": "One of the oldest horse breeds, known for endurance and distinctive head shape.",
            "average_height": "14.1-15.1 hands",
            "average_weight": "800-1000 lbs",
            "temperament": "Intelligent, spirited, gentle",
            "primary_use": "Endurance, show, breeding",
            "is_active": True
        },
        {
            "name": "Thoroughbred",
            "origin_country": "England",
            "description": "Breed developed for horse racing, known for speed and agility.",
            "average_height": "15.2-16.2 hands",
            "average_weight": "1000-1200 lbs",
            "temperament": "Hot-blooded, energetic, athletic",
            "primary_use": "Racing, sport horse",
            "is_active": True
        },
        {
            "name": "Quarter Horse",
            "origin_country": "United States",
            "description": "America's most popular breed, excellent for western riding and ranch work.",
            "average_height": "14.3-16 hands",
            "average_weight": "950-1200 lbs",
            "temperament": "Calm, versatile, willing",
            "primary_use": "Western riding, ranch work, racing",
            "is_active": True
        },
        {
            "name": "Clydesdale",
            "origin_country": "Scotland",
            "description": "Large draft horse known for strength and distinctive feathered legs.",
            "average_height": "16-18 hands",
            "average_weight": "1800-2000 lbs",
            "temperament": "Gentle, willing, intelligent",
            "primary_use": "Draft work, show, driving",
            "is_active": True
        },
        {
            "name": "Friesian",
            "origin_country": "Netherlands",
            "description": "Elegant black horse with flowing mane and tail, known for high-stepping gait.",
            "average_height": "15.3-17 hands",
            "average_weight": "1200-1400 lbs",
            "temperament": "Gentle, willing, intelligent",
            "primary_use": "Dressage, driving, show",
            "is_active": True
        }
    ]
    
    try:
        # Add sample breeds to database
        for breed_data in sample_breeds:
            breed = HorseBreed(**breed_data)
            db.add(breed)
        
        db.commit()
        print(f"Successfully added {len(sample_breeds)} horse breeds to the database!")
        
        # Display added breeds
        print("\nAdded breeds:")
        for breed in db.query(HorseBreed).all():
            print(f"- {breed.name} ({breed.origin_country})")
            
    except Exception as e:
        db.rollback()
        print(f"Error adding sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()