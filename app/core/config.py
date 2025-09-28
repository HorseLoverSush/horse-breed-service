from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Horse Breed Service")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database Configuration - Uses environment variables for security
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5433"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "horse_breeds_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "horselover")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    AUTO_CREATE_TABLES: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
    RECREATE_TABLES: bool = os.getenv("RECREATE_TABLES", "false").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        # URL encode the password to handle special characters like @
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Security - All values now loaded from environment variables
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS Settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from environment variable."""
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    def __post_init__(self):
        """Validate required configuration after initialization."""
        # Validate required environment variables
        if not self.DATABASE_PASSWORD:
            raise ValueError("DATABASE_PASSWORD environment variable is required")
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY environment variable must be at least 32 characters long")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Enable validation
        validate_assignment = True


# Create global settings instance
settings = Settings()

# Validate configuration on startup
try:
    settings.__post_init__()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    print("📝 Please check your .env file or environment variables")
    print("💡 Copy .env.example to .env and update with your values")
    raise