from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_prefix="COMMONPLACE_",
    )

    root: Path = Field(description="The root path")
    wrap: int = Field(default=80, description="Target characters per line")
