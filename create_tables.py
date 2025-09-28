# Database Migration Script (OPTIONAL)
# This script manually creates the database tables based on the SQLAlchemy models
# 
# NOTE: This script is OPTIONAL because the application automatically creates
# tables on startup when AUTO_CREATE_TABLES=True in settings.
# 
# Use this script only when you need to:
# - Manually create tables without starting the application
# - Force recreation of tables
# - Debug database schema issues

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.database import Base
from app.models.horse_breed import HorseBreed  # Import all models here

def create_tables():
    """Create all tables in the database."""
    print("Creating database tables manually...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("\nNOTE: Tables are also automatically created when starting the application")
    print("if AUTO_CREATE_TABLES=True in settings (default behavior).")

if __name__ == "__main__":
    create_tables()