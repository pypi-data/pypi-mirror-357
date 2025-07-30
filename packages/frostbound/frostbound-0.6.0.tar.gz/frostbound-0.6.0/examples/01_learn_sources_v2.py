from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TypeAlias

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.pretty import pprint

from frostbound.pydanticonf.loader import ConfigLoader
from frostbound.pydanticonf.sources import (
    EnvironmentConfigSource,
    YamlConfigSource,
)

console = Console()

ConfigValue: TypeAlias = str | int | bool | float | list[str] | dict[str, str | int | bool]
ConfigDict: TypeAlias = dict[str, ConfigValue]
EnvVarsDict: TypeAlias = dict[str, str]


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = "admin"
    password: str = "default_password"
    ssl_enabled: bool = False


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    debug: bool = False


class AppSettings(BaseSettings):
    app_name: str = "My App"
    version: str = "1.0.0"
    database: DatabaseConfig = DatabaseConfig()
    server: ServerConfig = ServerConfig()

    model_config = SettingsConfigDict(case_sensitive=False)


def experiment_1_yaml_only() -> None:
    """Experiment 1: Load configuration from YAML only."""
    console.print("🧪 Experiment 1: YAML Configuration Only")

    yaml_config: ConfigDict = {
        "app_name": "YAML App",
        "version": "2.0.0",
        "database": {
            "host": "yaml-db.example.com",
            "port": 5432,
            "username": "yaml_user",
            "password": "yaml_password",
            "ssl_enabled": True,
        },
        "server": {"host": "0.0.0.0", "port": 9000, "workers": 4, "debug": False},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        import yaml

        yaml.dump(yaml_config, f)
        yaml_path = Path(f.name)

    try:
        settings = ConfigLoader.from_yaml(AppSettings, yaml_path)  # type: ignore[attr-defined]

        console.print("📥 Loaded settings:")
        pprint(settings)

        console.print(f"\n✅ App: {settings.app_name} v{settings.version}")
        console.print(f"✅ Database: {settings.database.host}:{settings.database.port}")
        console.print(f"✅ Server: {settings.server.host}:{settings.server.port}")

    finally:
        yaml_path.unlink()

    console.print()


def experiment_2_environment_only() -> None:
    """Experiment 2: Load configuration from environment variables only."""
    console.print("🧪 Experiment 2: Environment Variables Only")

    # Save original environment
    original_env = dict(os.environ)

    try:
        # Set environment variables
        env_vars: EnvVarsDict = {
            "EXP_APP_NAME": "Environment App",
            "EXP_VERSION": "3.0.0",
            "EXP_DATABASE__HOST": "env-db.example.com",
            "EXP_DATABASE__PORT": "3306",
            "EXP_DATABASE__USERNAME": "env_user",
            "EXP_DATABASE__PASSWORD": "env_secret",
            "EXP_DATABASE__SSL_ENABLED": "true",
            "EXP_SERVER__PORT": "8080",
            "EXP_SERVER__WORKERS": "2",
            "EXP_SERVER__DEBUG": "true",
        }

        os.environ.update(env_vars)

        # Load using ConfigLoader
        settings = ConfigLoader.from_env(AppSettings, env_prefix="EXP")  # type: ignore[attr-defined]

        console.print("📥 Loaded settings:")
        pprint(settings)

        console.print(f"\n✅ App: {settings.app_name} v{settings.version}")
        console.print(f"✅ Database: {settings.database.host}:{settings.database.port}")
        console.print(f"✅ Server: {settings.server.host}:{settings.server.port}")

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def experiment_3_yaml_plus_environment() -> None:
    """Experiment 3: YAML + Environment (the real-world pattern)."""
    console.print("🧪 Experiment 3: YAML + Environment Variables")

    # YAML provides defaults and structure
    yaml_config: ConfigDict = {
        "app_name": "Hybrid App",
        "version": "1.0.0",
        "database": {
            "host": "default-db.example.com",
            "port": 5432,
            "username": "default_user",
            # Note: no password in YAML (security!)
            "ssl_enabled": False,
        },
        "server": {"host": "0.0.0.0", "port": 8000, "workers": 1, "debug": False},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        import yaml

        yaml.dump(yaml_config, f)
        yaml_path = Path(f.name)

    original_env = dict(os.environ)

    try:
        # Environment provides secrets and overrides
        env_vars: EnvVarsDict = {
            # Secrets (not in YAML)
            "HYBRID_DATABASE__PASSWORD": "super_secret_password",
            # Production overrides
            "HYBRID_DATABASE__HOST": "prod-db.example.com",
            "HYBRID_DATABASE__SSL_ENABLED": "true",
            "HYBRID_SERVER__WORKERS": "8",
            "HYBRID_SERVER__DEBUG": "false",
            # New configuration not in YAML
            "HYBRID_VERSION": "2.1.0",
        }

        os.environ.update(env_vars)

        console.print("📝 YAML configuration:")
        pprint(yaml_config)

        console.print("\n🌍 Environment overrides:")
        for key, value in env_vars.items():
            console.print(f"   {key}={value}")

        # Load using the convenient helper method
        settings = ConfigLoader.from_yaml_with_env(  # type: ignore[attr-defined]
            AppSettings, yaml_path=yaml_path, env_prefix="HYBRID"
        )

        console.print("\n📥 Final merged settings:")
        pprint(settings)

        console.print(f"\n✅ App: {settings.app_name} v{settings.version}")
        console.print(f"✅ Database: {settings.database.username}@{settings.database.host}:{settings.database.port}")
        console.print(f"✅ Database SSL: {settings.database.ssl_enabled}")
        console.print(f"✅ Database Password: {'***' if settings.database.password else 'None'}")
        console.print(f"✅ Server: {settings.server.host}:{settings.server.port} ({settings.server.workers} workers)")

    finally:
        yaml_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def experiment_4_multiple_sources() -> None:
    """Experiment 4: Multiple sources with custom merging order."""
    console.print("🧪 Experiment 4: Multiple Sources with Custom Order")

    # Base configuration
    base_config: ConfigDict = {
        "app_name": "Base App",
        "database": {"host": "base-db", "port": 5432},
        "server": {"port": 8000, "workers": 1},
    }

    # Development overrides
    dev_config: ConfigDict = {
        "app_name": "Dev App",
        "database": {"host": "dev-db", "ssl_enabled": False},
        "server": {"debug": True},
    }

    # Production overrides
    prod_config: ConfigDict = {
        "database": {"host": "prod-db", "ssl_enabled": True},
        "server": {"workers": 8, "debug": False},
    }

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        import yaml

        yaml.dump(base_config, f1)
        base_path = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        yaml.dump(dev_config, f2)
        dev_path = Path(f2.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f3:
        yaml.dump(prod_config, f3)
        prod_path = Path(f3.name)

    original_env = dict(os.environ)

    try:
        # Environment variables (highest priority)
        env_vars: EnvVarsDict = {"MULTI_DATABASE__PASSWORD": "env_secret", "MULTI_SERVER__PORT": "9000"}

        os.environ.update(env_vars)

        # Create sources
        base_source = YamlConfigSource(base_path)
        dev_source = YamlConfigSource(dev_path)
        prod_source = YamlConfigSource(prod_path)
        env_source = EnvironmentConfigSource(prefix="MULTI")

        console.print("📝 Base config:")
        pprint(base_source.load())

        console.print("\n📝 Dev config:")
        pprint(dev_source.load())

        console.print("\n📝 Prod config:")
        pprint(prod_source.load())

        console.print("\n🌍 Environment config:")
        pprint(env_source.load())

        # Scenario 1: Development setup (base + dev + env)
        console.print("\n🔧 Development setup (base → dev → env):")
        dev_settings = ConfigLoader.from_sources(  # type: ignore[attr-defined]
            AppSettings, base_source, dev_source, env_source
        )
        pprint(dev_settings)

        # Scenario 2: Production setup (base + prod + env)
        console.print("\n🏭 Production setup (base → prod → env):")
        prod_settings = ConfigLoader.from_sources(  # type: ignore[attr-defined]
            AppSettings, base_source, prod_source, env_source
        )
        pprint(prod_settings)

        console.print("\n💡 Notice the differences:")
        console.print(f"   Dev app_name: {dev_settings.app_name}")
        console.print(f"   Prod app_name: {prod_settings.app_name}")
        console.print(f"   Dev debug: {dev_settings.server.debug}")
        console.print(f"   Prod debug: {prod_settings.server.debug}")
        console.print(f"   Dev workers: {dev_settings.server.workers}")
        console.print(f"   Prod workers: {prod_settings.server.workers}")

    finally:
        base_path.unlink()
        dev_path.unlink()
        prod_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def main() -> None:
    """Run all experiments."""
    console.print("🔬 Configuration Sources Experiments\n")
    console.print("This file demonstrates different ways to use the sources.")
    console.print("Feel free to modify the configurations and re-run!\n")

    experiment_1_yaml_only()
    experiment_2_environment_only()
    experiment_3_yaml_plus_environment()
    experiment_4_multiple_sources()

    console.print("🎉 All experiments complete!")
    console.print("\n💡 Try modifying the configurations above and running again!")
    console.print("   • Change values in the YAML configs")
    console.print("   • Add/remove environment variables")
    console.print("   • Change the order of sources in experiment 4")
    console.print("   • Add new fields to the Pydantic models")


if __name__ == "__main__":
    main()
