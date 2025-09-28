from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Horse Breed Service"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5433
    DATABASE_NAME: str = "horse_breeds_db"
    DATABASE_USER: str = "horselover"
    DATABASE_PASSWORD: str = "monkhorselover@2025"
    AUTO_CREATE_TABLES: bool = True  # Automatically create tables on startup
    
    @property
    def DATABASE_URL(self) -> str:
        # URL encode the password to handle special characters like @
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()