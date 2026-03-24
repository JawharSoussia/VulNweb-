"""Application Configuration"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "VulNweb"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (will add in Phase 3.5)
    database_url: str = "postgresql://user:password@localhost:5432/vulnweb"
    db_echo: bool = False

    # Model
    model_path: str = "ml_model/inference/models/xgboost_smote_model.pkl"
    preprocessor_path: str = "ml_model/training/preprocessor.pkl"

    # API
    api_timeout: int = 30
    max_batch_size: int = 100

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()