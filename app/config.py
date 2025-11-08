"""
Configuration settings for SimpleAgent
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys (set via environment variables)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Model preferences
    DEFAULT_MODEL: str = "gpt-4"
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Output settings
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Agent settings
    ENABLE_CODE_GENERATION: bool = True
    CODE_GENERATION_THRESHOLD: float = 0.3 # Confidence threshold for code generation
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


