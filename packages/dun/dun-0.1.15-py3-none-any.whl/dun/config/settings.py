"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic.env_settings import SettingsSourceCallable
from pydantic_settings import BaseSettings

from dun.core.protocols import ConfigProtocol


def env_file_settings(settings: BaseSettings) -> Dict[str, Any]:
    """Load settings from .env file."""
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    return {}


class AppSettings(BaseSettings, ConfigProtocol):
    """Application settings with support for environment variables and .env files."""
    
    # Application settings
    APP_NAME: str = "Dun"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # File system settings
    BASE_DIR: Path = Path.cwd()
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    CACHE_DIR: Path = BASE_DIR / ".cache"
    
    # Ollama settings
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 30
    
    # File processing
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: list[str] = ["csv", "json", "txt"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize settings sources."""
            return env_file_settings, env_settings, init_settings, file_secret_settings
    
    @validator("BASE_DIR", "DATA_DIR", "LOGS_DIR", "CACHE_DIR", pre=True)
    def ensure_paths_exist(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v = Path(v).resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if hasattr(self, key):
            setattr(self, key, value)
    
    def load(self) -> None:
        """Load configuration from environment variables."""
        # Pydantic loads from env automatically
        pass
    
    def save(self) -> None:
        """Save configuration to .env file."""
        env_path = Path.cwd() / '.env'
        with open(env_path, 'w') as f:
            for field in self.__fields__:
                if field.isupper() and field != 'CONFIG':
                    value = getattr(self, field)
                    if value is not None:
                        f.write(f"{field}={value}\n")


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get the global settings instance."""
    return settings
