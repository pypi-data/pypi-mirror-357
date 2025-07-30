import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.pretty import pprint

from frostbound.pydanticonf import ConfigLoader, EnvironmentConfigSource, YamlConfigSource

os.environ["DEV_DB__PASSWORD"] = "super-secret-db-password-123!"


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str


class OptimizerConfig(BaseModel):
    algorithm: str
    learning_rate: float


class Settings(BaseSettings):
    app_name: str
    db: DatabaseConfig
    optimizer: OptimizerConfig

    model_config = SettingsConfigDict(
        env_prefix="DEV",
        env_file=".env.sample",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


# Option 1: Use Pydantic native loading (respects .env.sample file) with YAML overrides
settings = ConfigLoader.from_pydantic_native(settings_class=Settings, yaml_path=Path("./examples/simple_config.yaml"))

pprint(settings)

# Option 2: Use explicit sources (ignores .env.sample file)
yaml_source = YamlConfigSource(Path("./examples/simple_config.yaml"))
env_source = EnvironmentConfigSource(prefix="DEV")
pprint(yaml_source.load())
pprint(env_source.load())
settings = ConfigLoader.from_explicit_sources(Settings, [yaml_source, env_source])

pprint(settings)
