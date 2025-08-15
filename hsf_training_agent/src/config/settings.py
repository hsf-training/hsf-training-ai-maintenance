"""Configuration management for HSF Training Agent."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY", description="Google Gemini API key")
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN", description="GitHub API token")
    
    # Application settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_file_size_mb: int = Field(10, env="MAX_FILE_SIZE_MB")
    analysis_timeout_seconds: int = Field(300, env="ANALYSIS_TIMEOUT_SECONDS")
    
    # File processing
    supported_extensions: list[str] = [".md", ".ipynb", ".rst", ".txt"]
    ignore_patterns: list[str] = ["*.git*", "*.pyc", "__pycache__", "node_modules"]
    
    # AI Model settings
    gemini_model: str = "gemini-2.0-flash"
    max_tokens: int = 8192
    temperature: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    
    if env_path:
        load_dotenv(env_path)
    else:
        # Look for .env in current directory or parent directories
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            env_file = parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                break