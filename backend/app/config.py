import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartPlacement API"
    API_V1_STR: str = "/api"
    
    # Database configuration
    # Supports PostgreSQL / Supabase, falls back to local SQLite if not configured
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smartplacement.db")
    
    # Supabase credentials (optional if connecting directly or via REST)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
