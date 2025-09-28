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
            "food_requirements": "High-quality hay, grain, and grass. Requires 2-3% of body weight in feed daily.",
            "exercise_needs": "Daily exercise essential. Excellent for long-distance riding and endurance activities.",
            "common_health_issues": "Generally healthy. Watch for colic, metabolic issues, and genetic conditions.",
            "habitat_requirements": "Adaptable to various climates. Needs shelter, clean water, and adequate pasture.",
            "grooming_needs": "Daily brushing recommended. Regular hoof care and mane/tail maintenance.",
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
            "food_requirements": "High-energy diet with quality grain, hay, and supplements. 3-4% of body weight daily.",
            "exercise_needs": "High exercise requirements. Daily training, galloping, and conditioning work.",
            "common_health_issues": "Prone to bleeding disorders, fractures, and respiratory issues.",
            "habitat_requirements": "Well-ventilated stables, quality pasture, and access to training facilities.",
            "grooming_needs": "Daily grooming essential. Special attention to legs and hooves.",
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
            "food_requirements": "Moderate feed requirements. Quality hay, grass, and grain as needed.",
            "exercise_needs": "Moderate to high. Excellent for trail riding, ranch work, and western sports.",
            "common_health_issues": "Generally hardy. Watch for HYPP, navicular syndrome, and laminitis.",
            "habitat_requirements": "Very adaptable. Comfortable in various environments with basic shelter.",
            "grooming_needs": "Regular brushing and hoof care. Low-maintenance coat.",
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
            "food_requirements": "Large appetite due to size. High-quality hay, grain, and pasture. 3-4% of body weight.",
            "exercise_needs": "Moderate exercise. Strong but not high-energy. Enjoys driving and light draft work.",
            "common_health_issues": "Prone to chronic progressive lymphedema and joint issues due to size.",
            "habitat_requirements": "Large, sturdy shelter needed. Ample pasture space and clean, dry footing.",
            "grooming_needs": "Daily care of feathered legs essential. Regular brushing and hoof maintenance.",
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
            "food_requirements": "Quality hay and grass. Moderate grain needs. Monitor weight carefully.",
            "exercise_needs": "Moderate exercise. Excellent for dressage, driving, and light riding.",
            "common_health_issues": "Prone to dwarfism, aortic rupture, and chronic scratches.",
            "habitat_requirements": "Prefers cooler climates. Needs good shelter and well-drained pastures.",
            "grooming_needs": "Extensive grooming required. Daily mane and tail care, regular bathing.",
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