import os
from pydantic_settings import BaseSettings

IS_VERCEL = bool(os.getenv("VERCEL"))

default_db_url = "sqlite:////tmp/finbank.db" if IS_VERCEL else "sqlite:///./finbank.db"
default_upload_dir = "/tmp/uploads" if IS_VERCEL else "./uploads"

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinBank AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # LLM Settings
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-mini-4b-instruct")
    NVIDIA_API_URL: str = os.getenv("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1")
    
    # Storage Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", default_db_url)
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", default_upload_dir)
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
