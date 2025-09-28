from sqlalchemy import create_engine, text, inspect
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


def recreate_tables():
    """Drop and recreate all tables (WARNING: This will delete all data!)"""
    try:
        # Import all models to ensure they're registered with Base
        from app.models.horse_breed import HorseBreed
        
        print("WARNING: Dropping all tables - this will delete all data!")
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped successfully!")
        
        # Recreate all tables with updated schema
        Base.metadata.create_all(bind=engine)
        print("Tables recreated with updated schema!")
    except Exception as e:
        print(f"Error recreating tables: {e}")


def migrate_schema():
    """Migrate database schema by adding missing columns (preserves data)."""
    try:
        # Import all models to ensure they're registered with Base  
        from app.models.horse_breed import HorseBreed
        
        print("Checking for schema changes...")
        
        # Get current table columns from database
        inspector = inspect(engine)
        existing_columns = set()
        
        if inspector.has_table('horse_breeds'):
            columns = inspector.get_columns('horse_breeds')
            existing_columns = {col['name'] for col in columns}
            print(f"Found existing columns: {existing_columns}")
        
        # Get expected columns from model
        model_columns = set()
        for column in HorseBreed.__table__.columns:
            model_columns.add(column.name)
        print(f"Expected columns from model: {model_columns}")
        
        # Find missing columns
        missing_columns = model_columns - existing_columns
        
        if missing_columns:
            print(f"Adding missing columns: {missing_columns}")
            
            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    for column_name in missing_columns:
                        # Get column definition from model
                        model_column = HorseBreed.__table__.columns[column_name]
                        
                        # Build ALTER TABLE statement
                        column_type = model_column.type.compile(engine.dialect)
                        nullable = "NULL" if model_column.nullable else "NOT NULL"
                        default_clause = ""
                        
                        if model_column.default is not None:
                            if hasattr(model_column.default, 'arg'):
                                default_value = model_column.default.arg
                                if isinstance(default_value, bool):
                                    default_clause = f" DEFAULT {str(default_value).lower()}"
                                elif isinstance(default_value, str):
                                    default_clause = f" DEFAULT '{default_value}'"
                                else:
                                    default_clause = f" DEFAULT {default_value}"
                        
                        alter_sql = f"ALTER TABLE horse_breeds ADD COLUMN {column_name} {column_type}{default_clause}"
                        
                        print(f"Executing: {alter_sql}")
                        conn.execute(text(alter_sql))
                        print(f"✅ Added column: {column_name}")
                    
                    trans.commit()
                    print("Schema migration completed successfully!")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Error during migration: {e}")
                    raise
        else:
            print("✅ Schema is up to date - no migration needed!")
            
    except Exception as e:
        print(f"Error during schema migration: {e}")


def init_database():
    """Initialize database - create tables if needed and migrate schema."""
    if settings.RECREATE_TABLES:
        recreate_tables()
    elif settings.AUTO_CREATE_TABLES:
        create_tables()
        # Always check for schema migrations after creating/checking tables
        migrate_schema()


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