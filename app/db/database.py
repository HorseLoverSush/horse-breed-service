from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def create_tables():
    """Create database tables if they don't exist."""
    try:
        # Import all models to ensure they're registered with Base
        from app.models.horse_breed import HorseBreed
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")


def init_database():
    """Initialize database - create tables if needed."""
    if settings.AUTO_CREATE_TABLES:
        create_tables()


# Dependency to get DB session
def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()