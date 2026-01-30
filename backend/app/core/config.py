"""
Application configuration using Pydantic Settings.

Loads environment variables and provides typed configuration.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "mingle"
    POSTGRES_PASSWORD: str = "mingle_secret"
    POSTGRES_DB: str = "mingle"
    
    @property
    def POSTGRES_URL(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # MongoDB
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "mingle"
    MONGODB_PASSWORD: str = "mingle_secret"
    MONGODB_DB: str = "mingle"
    
    @property
    def MONGODB_URL(self) -> str:
        """Construct MongoDB connection URL."""
        return (
            f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
            f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}"
        )
    
    # ClickHouse
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_HTTP_PORT: int = 8123
    CLICKHOUSE_NATIVE_PORT: int = 9000
    CLICKHOUSE_USER: str = "mingle"
    CLICKHOUSE_PASSWORD: str = "mingle_secret"
    CLICKHOUSE_DB: str = "mingle_analytics"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string if needed."""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
