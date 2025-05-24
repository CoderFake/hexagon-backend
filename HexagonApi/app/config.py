import os
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Optional, Union

from app.ext.firebase.base import FirebaseAdminSettings, FirebaseAuthSettings
from app.ext.email.base import SendEmailSettings
from app.ext.storage.base import StorageSettings
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    """
    Application configuration settings.
    """

    class DB(BaseModel):
        """
        Database connection configuration.
        """

        dsn: str = Field(description="Database DSN connection string.")
        pool_size: int = Field(default=20, description="Maximum connection pool size.")
        echo: bool = Field(default=False, description="Whether to output query logs.")
        echo_pool: bool = Field(default=False, description="Whether to output connection pool-related logs.")


    class Static(BaseModel):
        """
        Static file distribution configuration.
        """

        root: str = Field(description="Root directory.")
        path: str = Field(description="URL path.")

    class SetTimeZone(BaseModel):
        timezone: str = Field()

    class DocumentAuth(BaseModel):
        """
        Documentation authentication configuration.
        """
        enabled: bool = Field(default=True, description="Enable documentation endpoints")
        username: Optional[str] = Field(default=None, description="Basic auth username for docs")
        password: Optional[str] = Field(default=None, description="Basic auth password for docs")

    # Application settings
    name: str = Field(description="Application name.")
    version: str = Field(description="Application version.")
    env: str = Field(default="dev", description="Environment: dev, stg, prod")
    errors: Optional[str] = Field(default=None, description="Error message configuration file path.")
    launch_screen: bool = Field(default=False, description="Flag to show launch screen.")
    
    # Sub-configurations
    static: Optional[Static] = Field(default=None)
    db: DB
    storage: StorageSettings
    firebase: Union[FirebaseAuthSettings, FirebaseAdminSettings]
    email: SendEmailSettings
    tz: SetTimeZone
    docs: DocumentAuth = Field(default_factory=DocumentAuth)

    def dump(self) -> str:
        lines = ["[root]"]

        for n, f in self.model_fields.items():
            value = getattr(self, n)

            if isinstance(value, BaseModel):
                lines.append(f"[{n}]")
                for k, v in value.model_dump().items():
                    lines.append(f"{(k+':'):16}{v}")
            else:
                lines.append(f"{(n+':'):16}{value}")

        return "\n".join(lines)


@lru_cache
def get_project_root() -> Path:
    """
    Get the project root directory (hexagon-backend).
    """
    current_file = Path(__file__)
    return current_file.parent.parent.parent


@lru_cache
def get_env_file_path() -> Path:
    """
    Get the .env file path from project root.
    """
    return get_project_root() / ".env"


class Environment:
    """
    Environment configuration loader.
    """

    def __init__(self, delimiter: str = "__") -> None:
        self.delimiter = delimiter
        self.env_file = get_env_file_path()

    @cached_property
    def settings(self) -> ApplicationSettings:
        """
        Load application settings from .env file in project root.
        """
        if not self.env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {self.env_file}")
        
        local_env = self.env_file.with_suffix(".env.local")
        
        env_files = [str(self.env_file)]
        if local_env.exists():
            env_files.append(str(local_env))

        settings = ApplicationSettings(
            _env_file=env_files,
            _env_nested_delimiter=self.delimiter,
        )
        
        self._configure_for_environment(settings)
        
        return settings
    
    def _configure_for_environment(self, settings: ApplicationSettings) -> None:
        """Configure settings based on environment."""
        if self.is_development:
            settings.docs.enabled = True
            settings.docs.username = None
            settings.docs.password = None
        elif self.is_staging or self.is_production:
            settings.docs.enabled = True
            if not settings.docs.username:
                settings.docs.username = os.environ.get("DOCS_USERNAME", "admin")
            if not settings.docs.password:
                settings.docs.password = os.environ.get("DOCS_PASSWORD", "admin123")

    @property
    def env_name(self) -> str:
        """Get environment name from ENV variable or default to 'dev'."""
        return os.environ.get("ENV", "dev")

    @property 
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env_name == "dev"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment.""" 
        return self.env_name == "stg"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env_name == "prod"


@lru_cache
def environment() -> Environment:
    """
    Get the environment configuration.
    """
    return Environment()


@lru_cache
def settings() -> ApplicationSettings:
    """
    Get application settings (shortcut function).
    """
    return environment().settings
