"""
Example 08: Comprehensive ConfigLoader Showcase
Demonstrates ALL permutations and features of the ConfigLoader system
"""

import os
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.table import Table

from frostbound.pydanticonf import ConfigLoader, instantiate

console = Console()


# =============================================================================
# Configuration Models
# =============================================================================


class DatabaseConfig(BaseModel):
    """Database configuration model."""

    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: str = "password"
    pool_size: int = 10
    ssl: bool = False


class CacheConfig(BaseModel):
    """Cache configuration model."""

    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000
    backend: str = "redis"
    redis: dict[str, Any] = Field(default_factory=lambda: {"host": "localhost", "port": 6379})


class MLModelConfig(BaseModel):
    """ML model configuration with instantiation support."""

    _target_: Optional[str] = None
    name: str = "default_model"
    input_dim: int = 100
    hidden_dim: int = 50
    output_dim: int = 10
    activation: str = "relu"
    dropout: float = 0.1


class ServiceConfig(BaseModel):
    """Service configuration with nested components."""

    name: str = "ml_service"
    version: str = "1.0.0"
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    model: MLModelConfig = Field(default_factory=MLModelConfig)
    features: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# Get the directory for env files
_SCRIPT_DIR = Path(__file__).parent


# Settings classes with different configurations
class BasicSettings(BaseSettings):
    """Basic settings without env_file."""

    model_config = SettingsConfigDict(
        extra="ignore"  # Ignore extra fields from YAML/env
    )

    app_name: str = "BasicApp"
    debug: bool = False
    port: int = 8000
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)


class PydanticNativeSettings(BaseSettings):
    """Settings with Pydantic's env_file configured."""

    model_config = SettingsConfigDict(
        env_file=str(_SCRIPT_DIR / ".env"),
        env_prefix="APP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "PydanticApp"
    debug: bool = False
    port: int = 8000
    secret_key: str = "default-secret"
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)


class MultiEnvSettings(BaseSettings):
    """Settings with multiple env files."""

    model_config = SettingsConfigDict(
        env_file=[str(_SCRIPT_DIR / ".env"), str(_SCRIPT_DIR / ".env.prod")],  # Multiple files
        env_prefix="MULTI_",
        extra="ignore",
    )

    app_name: str = "MultiEnvApp"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    workers: int = 1
    ssl_enabled: bool = False


# =============================================================================
# Mock Classes for Instantiation Demo
# =============================================================================


class NeuralNetwork:
    """Mock neural network for instantiation demo."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        activation: str = "relu",
        dropout: float = 0.1,
        name: str = "nn",
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.activation = activation
        self.dropout = dropout
        self.name = name

    def __repr__(self):
        return f"NeuralNetwork({self.input_dim}→{self.hidden_dim}→{self.output_dim}, {self.activation})"


class DataProcessor:
    """Mock data processor for instantiation demo."""

    def __init__(self, normalize: bool = True, features: list[str] = None, cache: Optional[dict] = None):
        self.normalize = normalize
        self.features = features or []
        self.cache = cache

    def __repr__(self):
        return f"DataProcessor(normalize={self.normalize}, features={len(self.features)})"


# =============================================================================
# Main Showcase
# =============================================================================


def showcase_configloader():
    """Comprehensive showcase of ConfigLoader features."""

    console.print(
        Panel.fit(
            "🎯 Comprehensive ConfigLoader Showcase\n\n"
            "This example demonstrates ALL permutations of ConfigLoader:\n"
            "• 📄 All loading methods (from_yaml_with_env, from_yaml, from_env, from_sources)\n"
            "• 🔀 Pydantic-native vs Source composition modes\n"
            "• 🎭 Hybrid behavior and mode detection\n"
            "• 📊 Precedence rules in different modes\n"
            "• 🔧 Object instantiation support\n"
            "• 🌍 Environment variable handling with nested delimiters\n"
            "• ⚡ All edge cases and features!",
            title="ConfigLoader Showcase",
            style="bold blue",
        )
    )

    # Get script directory for file paths
    script_dir = Path(__file__).parent

    # ==========================================================================
    # PART 1: Basic Loading Methods
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 1: Basic Loading Methods[/bold cyan]")
    console.print("=" * 80)

    # 1.1 from_yaml - YAML only
    console.print("\n[yellow]1.1 ConfigLoader.from_yaml() - YAML only:[/yellow]")
    settings_yaml_only = ConfigLoader.from_yaml(BasicSettings, script_dir / "config.yaml")
    console.print("Loaded from config.yaml:")
    pprint(settings_yaml_only)

    # 1.2 from_env - Environment only
    console.print("\n[yellow]1.2 ConfigLoader.from_env() - Environment variables only:[/yellow]")
    # Set some env vars
    os.environ["TEST_APP_NAME"] = "EnvOnlyApp"
    os.environ["TEST_DEBUG"] = "true"
    os.environ["TEST_PORT"] = "9000"
    os.environ["TEST_DATABASE__HOST"] = "env-db-host"
    os.environ["TEST_DATABASE__PORT"] = "5433"
    os.environ["TEST_CACHE__ENABLED"] = "false"
    os.environ["TEST_CACHE__REDIS__HOST"] = "env-redis"

    settings_env_only = ConfigLoader.from_env(BasicSettings, env_prefix="TEST_", env_nested_delimiter="__")
    console.print("Loaded from TEST_* environment variables:")
    pprint(settings_env_only)
    console.print("\n[dim]Note: Nested delimiter '__' created nested structure![/dim]")

    # Clean up env vars
    for key in list(os.environ.keys()):
        if key.startswith("TEST_"):
            del os.environ[key]

    # 1.3 from_sources - Custom source composition
    console.print("\n[yellow]1.3 ConfigLoader.from_sources() - Custom source composition:[/yellow]")
    from frostbound.pydanticonf.sources import EnvironmentConfigSource, YamlConfigSource

    yaml_source = YamlConfigSource(script_dir / "config.yaml")
    env_source = EnvironmentConfigSource("CUSTOM_", "__")

    # Set custom env vars
    os.environ["CUSTOM_PORT"] = "7777"
    os.environ["CUSTOM_CACHE__TTL"] = "7200"

    settings_custom = ConfigLoader.from_sources(BasicSettings, yaml_source, env_source)
    console.print("Loaded from custom sources (YAML + CUSTOM_* env vars):")
    pprint(settings_custom)

    # Clean up
    del os.environ["CUSTOM_PORT"]
    del os.environ["CUSTOM_CACHE__TTL"]

    # ==========================================================================
    # PART 2: Pydantic-native Mode (Auto-detection)
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 2: Pydantic-native Mode (Auto-detection)[/bold cyan]")
    console.print("=" * 80)

    # 2.1 Basic Pydantic-native loading
    console.print("\n[yellow]2.1 Pydantic-native mode - env_file detected:[/yellow]")
    console.print("[dim]PydanticNativeSettings has env_file='.env' configured[/dim]")

    settings_native = ConfigLoader.from_yaml_with_env(PydanticNativeSettings)
    console.print("\nLoaded with Pydantic handling .env:")
    pprint(settings_native)

    # 2.2 Pydantic-native + YAML override
    console.print("\n[yellow]2.2 Pydantic-native + YAML override:[/yellow]")
    settings_native_yaml = ConfigLoader.from_yaml_with_env(PydanticNativeSettings, yaml_path=script_dir / "config.yaml")
    console.print("Loaded with .env + config.yaml override:")
    pprint(settings_native_yaml)
    console.print("\n[dim]Note: YAML overrides values from .env![/dim]")

    # 2.3 Multiple env files
    console.print("\n[yellow]2.3 Multiple env files:[/yellow]")
    settings_multi = ConfigLoader.from_yaml_with_env(MultiEnvSettings)
    console.print("Loaded from [.env, .env.prod]:")
    pprint(settings_multi)
    console.print("\n[dim]Note: Later files override earlier ones![/dim]")

    # ==========================================================================
    # PART 3: Source Composition Mode (No env_file)
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 3: Source Composition Mode (No env_file)[/bold cyan]")
    console.print("=" * 80)

    # 3.1 Basic source composition
    console.print("\n[yellow]3.1 Source composition - no env_file:[/yellow]")
    console.print("[dim]BasicSettings has no env_file configured[/dim]")

    # Set env vars for composition mode
    os.environ["COMP_APP_NAME"] = "CompositionApp"
    os.environ["COMP_PORT"] = "6666"
    os.environ["COMP_DATABASE__HOST"] = "comp-db"
    os.environ["COMP_CACHE__BACKEND"] = "memcached"

    settings_comp = ConfigLoader.from_yaml_with_env(
        BasicSettings, yaml_path=script_dir / "config.yaml", env_prefix="COMP_", env_nested_delimiter="__"
    )
    console.print("Loaded with YAML + COMP_* env vars:")
    pprint(settings_comp)
    console.print("\n[dim]Note: Environment variables override YAML![/dim]")

    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith("COMP_"):
            del os.environ[key]

    # 3.2 Source composition with missing YAML
    console.print("\n[yellow]3.2 Source composition - missing YAML graceful handling:[/yellow]")
    settings_no_yaml = ConfigLoader.from_yaml_with_env(
        BasicSettings,
        yaml_path=script_dir / "non_existent.yaml",  # Doesn't exist
        env_prefix="BASIC_",
    )
    console.print("Loaded with missing YAML (falls back to env/defaults):")
    pprint(settings_no_yaml)

    # ==========================================================================
    # PART 4: Forced Composition Mode
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 4: Forced Composition Mode[/bold cyan]")
    console.print("=" * 80)

    console.print("\n[yellow]4.1 Force composition despite env_file:[/yellow]")
    console.print("[dim]PydanticNativeSettings has env_file, but we force composition[/dim]")

    # Set env vars
    os.environ["FORCE_APP_NAME"] = "ForcedComposition"
    os.environ["FORCE_SECRET_KEY"] = "forced-secret"

    settings_forced = ConfigLoader.from_yaml_with_env(
        PydanticNativeSettings,
        yaml_path=script_dir / "config.yaml",
        env_prefix="FORCE_",
        respect_pydantic_env_file=False,  # Force composition mode!
    )
    console.print("Loaded ignoring .env file:")
    pprint(settings_forced)
    console.print("\n[dim]Note: .env was ignored, only YAML + FORCE_* vars used![/dim]")

    # Clean up
    del os.environ["FORCE_APP_NAME"]
    del os.environ["FORCE_SECRET_KEY"]

    # ==========================================================================
    # PART 5: Precedence Demonstration
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 5: Precedence Rules[/bold cyan]")
    console.print("=" * 80)

    # Create precedence table
    table = Table(title="Configuration Precedence Rules")
    table.add_column("Mode", style="cyan")
    table.add_column("Precedence Order", style="green")
    table.add_column("Example", style="yellow")

    table.add_row(
        "Pydantic-native\n(with env_file)",
        "1. Class defaults\n2. .env file(s)\n3. Pydantic env vars\n4. YAML override",
        "defaults → .env → APP_* → config.yaml",
    )

    table.add_row(
        "Source composition\n(no env_file)",
        "1. Class defaults\n2. YAML file\n3. Environment variables",
        "defaults → config.yaml → PREFIX_*",
    )

    table.add_row(
        "Forced composition", "1. Class defaults\n2. YAML file\n3. Environment variables", "Ignores env_file completely"
    )

    console.print(table)

    # ==========================================================================
    # PART 6: Object Instantiation
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 6: Object Instantiation with _target_[/bold cyan]")
    console.print("=" * 80)

    # Create a config with instantiable objects
    class InstantiableSettings(BaseSettings):
        """Settings with instantiable components."""

        app_name: str = "InstantiableApp"

        # Instantiable model config
        model: dict[str, Any] = {
            "_target_": "__main__.NeuralNetwork",
            "name": "main_model",
            "input_dim": 128,
            "hidden_dim": 64,
            "output_dim": 10,
            "activation": "tanh",
            "dropout": 0.2,
        }

        # Instantiable processor config
        processor: dict[str, Any] = {
            "_target_": "__main__.DataProcessor",
            "normalize": True,
            "features": ["age", "income", "score"],
            "cache": {"enabled": True, "ttl": 3600},
        }

    console.print("\n[yellow]6.1 Loading settings with _target_ configs:[/yellow]")
    settings_inst = InstantiableSettings()
    console.print("Settings loaded:")
    pprint(settings_inst)

    console.print("\n[yellow]6.2 Instantiating objects:[/yellow]")

    # Instantiate model
    model = instantiate(settings_inst.model)
    console.print("\nInstantiated model:")
    pprint(model)
    console.print(f"Type: {type(model).__name__}")
    console.print(f"Repr: {model}")

    # Instantiate processor
    processor = instantiate(settings_inst.processor)
    console.print("\nInstantiated processor:")
    pprint(processor)
    console.print(f"Type: {type(processor).__name__}")
    console.print(f"Repr: {processor}")

    # ==========================================================================
    # PART 7: Advanced Features & Edge Cases
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 7: Advanced Features & Edge Cases[/bold cyan]")
    console.print("=" * 80)

    # 7.1 Empty/None configurations
    console.print("\n[yellow]7.1 Empty configurations:[/yellow]")

    class EmptySettings(BaseSettings):
        """Minimal settings."""

        value: str = "default"

    empty1 = ConfigLoader.from_yaml_with_env(EmptySettings, env_prefix="EMPTY_")
    console.print("Empty YAML path (None) with EMPTY_ prefix:")
    pprint(empty1)

    # 7.2 Complex nested structures
    console.print("\n[yellow]7.2 Complex nested structures:[/yellow]")

    # Set complex nested env vars
    os.environ["NESTED_SERVICE__NAME"] = "nested-service"
    os.environ["NESTED_SERVICE__DATABASE__HOST"] = "nested-db"
    os.environ["NESTED_SERVICE__DATABASE__PORT"] = "3306"
    os.environ["NESTED_SERVICE__CACHE__REDIS__HOST"] = "nested-redis"
    os.environ["NESTED_SERVICE__CACHE__REDIS__PORT"] = "6380"
    os.environ["NESTED_SERVICE__MODEL__HIDDEN_DIM"] = "128"

    settings_nested = ConfigLoader.from_env(BasicSettings, env_prefix="NESTED_", env_nested_delimiter="__")
    console.print("Deep nested environment variables:")
    pprint(settings_nested)

    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith("NESTED_"):
            del os.environ[key]

    # 7.3 Type conversion demonstration
    console.print("\n[yellow]7.3 Type conversion from environment:[/yellow]")

    # Set typed env vars
    os.environ["TYPED_PORT"] = "12345"  # String → int
    os.environ["TYPED_DEBUG"] = "false"  # String → bool
    os.environ["TYPED_CACHE__TTL"] = "7200"  # String → int
    os.environ["TYPED_SERVICE__MODEL__DROPOUT"] = "0.15"  # String → float

    settings_typed = ConfigLoader.from_env(PydanticNativeSettings, env_prefix="TYPED_", env_nested_delimiter="__")
    console.print("Type conversions from environment:")
    console.print(f"  port: {settings_typed.port} ({type(settings_typed.port).__name__})")
    console.print(f"  debug: {settings_typed.debug} ({type(settings_typed.debug).__name__})")
    console.print(f"  cache.ttl: {settings_typed.cache.ttl} ({type(settings_typed.cache.ttl).__name__})")
    console.print(
        f"  service.model.dropout: {settings_typed.service.model.dropout} ({type(settings_typed.service.model.dropout).__name__})"
    )

    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith("TYPED_"):
            del os.environ[key]

    # ==========================================================================
    # Summary
    # ==========================================================================

    console.print(
        Panel.fit(
            "✅ ConfigLoader Showcase Complete!\n\n"
            "We demonstrated:\n"
            "• All loading methods (from_yaml, from_env, from_sources, from_yaml_with_env)\n"
            "• Pydantic-native mode with automatic env_file detection\n"
            "• Source composition mode for explicit control\n"
            "• Forced composition mode to override detection\n"
            "• Precedence rules in different modes\n"
            "• Nested environment variables with delimiters\n"
            "• Object instantiation with _target_\n"
            "• Type conversion and validation\n"
            "• Edge cases and advanced features\n\n"
            "The ConfigLoader provides a flexible, powerful system for\n"
            "configuration management that works seamlessly with Pydantic!",
            title="🎯 Showcase Summary",
            style="bold green",
        )
    )


if __name__ == "__main__":
    showcase_configloader()
