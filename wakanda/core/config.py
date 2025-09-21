"""
Core configuration management for Wakanda Protocol
Handles environment variables, security settings, and service configurations
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Main application settings"""
    
    # Application
    app_name: str = Field(default="Wakanda Protocol", env="WAKANDA_APP_NAME")
    version: str = Field(default="0.1.0", env="WAKANDA_VERSION")
    debug: bool = Field(default=False, env="WAKANDA_DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="WAKANDA_HOST")
    port: int = Field(default=8000, env="WAKANDA_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="WAKANDA_LOG_LEVEL")
    log_format: str = Field(default="json", env="WAKANDA_LOG_FORMAT")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="WAKANDA_SECRET_KEY")
    algorithm: str = Field(default="HS256", env="WAKANDA_JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="WAKANDA_ACCESS_TOKEN_EXPIRE")
    encryption_key: Optional[str] = Field(default=None, env="WAKANDA_ENCRYPTION_KEY")
    
    # HSM Configuration
    hsm_enabled: bool = Field(default=False, env="WAKANDA_HSM_ENABLED")
    hsm_library_path: Optional[str] = Field(default=None, env="WAKANDA_HSM_LIBRARY_PATH")
    hsm_slot: Optional[int] = Field(default=None, env="WAKANDA_HSM_SLOT")
    hsm_pin: Optional[str] = Field(default=None, env="WAKANDA_HSM_PIN")
    
    # External API Keys
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    alphavantage_api_key: Optional[str] = Field(default=None, env="ALPHAVANTAGE_API_KEY")
    mastercard_api_key: Optional[str] = Field(default=None, env="MASTERCARD_API_KEY")
    weather_api_key: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    
    # Database
    database_url: str = Field(default="postgresql://localhost/wakanda", env="DATABASE_URL")
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_echo: bool = Field(default=False, env="DB_ECHO")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="WAKANDA_CORS_ORIGINS")
    
    # Feature flags
    enable_fintech: bool = Field(default=True, env="WAKANDA_ENABLE_FINTECH")
    enable_minerals: bool = Field(default=True, env="WAKANDA_ENABLE_MINERALS")
    enable_ai: bool = Field(default=True, env="WAKANDA_ENABLE_AI")
    enable_governance: bool = Field(default=True, env="WAKANDA_ENABLE_GOVERNANCE")
    enable_infrastructure: bool = Field(default=True, env="WAKANDA_ENABLE_INFRASTRUCTURE")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()