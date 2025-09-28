# Schema Update Script
# This script manually adds new columns to existing tables
# Use this when you've added new fields to your models

from sqlalchemy import create_engine, text
from app.core.config import settings

def update_horse_breeds_schema():
    """Add new columns to the horse_breeds table."""
    engine = create_engine(settings.DATABASE_URL)
    
    # New columns to add
    new_columns = [
        "food_requirements TEXT",
        "exercise_needs TEXT", 
        "common_health_issues TEXT",
        "habitat_requirements TEXT",
        "grooming_needs TEXT"
    ]
    
    print("Updating horse_breeds table schema...")
    print(f"Database: {settings.DATABASE_URL}")
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            for column_def in new_columns:
                column_name = column_def.split()[0]
                
                # Check if column already exists
                check_sql = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'horse_breeds' 
                AND column_name = :column_name
                """
                
                result = conn.execute(text(check_sql), {"column_name": column_name})
                exists = result.fetchone()
                
                if not exists:
                    # Add the column
                    alter_sql = f"ALTER TABLE horse_breeds ADD COLUMN {column_def}"
                    conn.execute(text(alter_sql))
                    print(f"✅ Added column: {column_name}")
                else:
                    print(f"⚠️  Column already exists: {column_name}")
            
            # Commit transaction
            trans.commit()
            print("\n🎉 Schema update completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error updating schema: {e}")
            raise

if __name__ == "__main__":
    update_horse_breeds_schema()