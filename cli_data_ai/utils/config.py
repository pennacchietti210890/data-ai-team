import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Base configuration
    APP_NAME: str = "Data Analyst CLI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str
    DATABASE_NAME: str

    # Metabase settings
    METABASE_URL: str
    METABASE_USER_NAME: str
    METABASE_PASSWORD: str

    # LLM Provider settings
    LLM_PROVIDER: Optional[str] = None  # Can be "openai" or "groq"
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v):
        if v not in ["openai", "groq", None]:
            raise ValueError("LLM_PROVIDER must be either 'openai', 'groq', or None")
        return v

    @model_validator(mode="after")
    def check_llm_api_keys(self):
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        if self.LLM_PROVIDER == "groq" and not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER is 'groq'")
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Return the settings instance."""
    return settings