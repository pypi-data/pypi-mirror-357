from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from frostbound.pydanticonf import ConfigLoader, DynamicConfig, instantiate


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    pool_size: int = 10


class OptimizerBase:
    def __init__(self, learning_rate: float) -> None:
        self.learning_rate = learning_rate
        print(f"{self.__class__.__name__} initialized with lr={learning_rate}")

    def step(self) -> None:
        print(f"{self.__class__.__name__} taking optimization step")


class SGD(OptimizerBase):
    def __init__(self, learning_rate: float, momentum: float = 0.9) -> None:
        super().__init__(learning_rate)
        self.momentum = momentum


class Adam(OptimizerBase):
    def __init__(self, learning_rate: float, beta1: float = 0.9, beta2: float = 0.999) -> None:
        super().__init__(learning_rate)
        self.beta1 = beta1
        self.beta2 = beta2


class OptimizerConfig(DynamicConfig[OptimizerBase]):
    learning_rate: float = Field(0.001, description="Learning rate")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
    )

    app_name: str = "DemoApp"
    debug: bool = False
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    optimizer: OptimizerConfig = Field(
        default_factory=lambda: OptimizerConfig(
            _target_="examples.config_loader_demo.Adam",
            learning_rate=0.001,
        )
    )


def main() -> None:
    print("=== ConfigLoader Factory Pattern Demo ===\n")

    # Example 1: Load from environment only
    print("1. Loading from environment variables:")
    import os

    os.environ["APP_APP_NAME"] = "ProductionApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_DATABASE__HOST"] = "prod.db.server"
    os.environ["APP_OPTIMIZER___TARGET_"] = '"examples.config_loader_demo.SGD"'
    os.environ["APP_OPTIMIZER__LEARNING_RATE"] = "0.01"

    settings = ConfigLoader.from_env(AppSettings, env_prefix="APP")
    print(f"   App: {settings.app_name}, Debug: {settings.debug}")
    print(f"   Database: {settings.database.host}:{settings.database.port}")
    print(f"   Optimizer LR: {settings.optimizer.learning_rate}")

    # Example 2: Load from YAML
    print("\n2. Loading from YAML file:")
    yaml_content = """app_name: YamlApp
debug: false
database:
    host: yaml.db.server
    port: 5433
    pool_size: 20
optimizer:
    _target_: examples.config_loader_demo.SGD
    learning_rate: 0.005
    momentum: 0.95"""

    yaml_path = Path("examples/app_config.yaml")
    yaml_path.write_text(yaml_content)

    settings = ConfigLoader.from_yaml(AppSettings, yaml_path)
    print(f"   App: {settings.app_name}, Debug: {settings.debug}")
    print(f"   Database pool size: {settings.database.pool_size}")

    # Example 3: YAML + Environment (env overrides)
    print("\n3. Loading from YAML + Environment:")
    settings = ConfigLoader.from_yaml_with_env(AppSettings, yaml_path, env_prefix="APP")
    print(f"   App: {settings.app_name} (overridden by env)")
    print(f"   Debug: {settings.debug} (overridden by env)")
    print(f"   Database host: {settings.database.host} (overridden by env)")
    print(f"   Database pool size: {settings.database.pool_size} (from yaml)")

    # Example 4: Instantiate optimizer
    print("\n4. Instantiating optimizer from config:")
    optimizer = instantiate(settings.optimizer)
    optimizer.step()

    # Cleanup
    yaml_path.unlink()
    for key in [
        "APP_APP_NAME",
        "APP_DEBUG",
        "APP_DATABASE__HOST",
        "APP_OPTIMIZER___TARGET_",
        "APP_OPTIMIZER__LEARNING_RATE",
    ]:
        os.environ.pop(key, None)

    print("\n✅ ConfigLoader demo complete!")


if __name__ == "__main__":
    main()
