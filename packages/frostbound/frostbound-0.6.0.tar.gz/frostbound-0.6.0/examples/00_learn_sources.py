from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TypeAlias

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.syntax import Syntax
from rich.table import Table

from frostbound.pydanticonf.sources import (
    CompositeConfigSource,
    EnvironmentConfigSource,
    YamlConfigSource,
)

console = Console()

ConfigValue: TypeAlias = str | int | bool | list[str] | dict[str, str | int | bool]
ConfigDict: TypeAlias = dict[str, ConfigValue]
EnvVarsDict: TypeAlias = dict[str, str]


def print_yaml_config(title: str, config_dict: ConfigDict, subtitle: str | None = None) -> None:
    """Helper function to print YAML configs with beautiful formatting."""
    yaml_string = yaml.dump(config_dict, default_flow_style=False, indent=2)
    syntax = Syntax(yaml_string, "yaml", theme="github-dark", line_numbers=False)
    panel = Panel(syntax, title=f"📄 {title}", subtitle=subtitle, border_style="blue")
    console.print(panel)


def print_env_vars(title: str, env_vars: EnvVarsDict, prefix: str | None = None) -> None:
    """Helper function to print environment variables in a nice table."""
    table = Table(title=f"🌍 {title}", show_header=True, header_style="bold magenta")
    table.add_column("Environment Variable", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Notes", style="dim")

    for key, value in env_vars.items():
        if prefix and not key.startswith(prefix) and key != "OTHER_VAR":
            continue

        notes = ""
        if prefix and not key.startswith(prefix):
            notes = "❌ Ignored (no prefix)"
        elif key.endswith("_PASSWORD"):
            notes = "🔒 Secret"
        elif key.endswith("_PORT"):
            notes = "🔢 Will be parsed as int"
        elif key.endswith("_DEBUG"):
            notes = "✅ Will be parsed as bool"

        table.add_row(key, str(value), notes)

    console.print(table)


def step_1_yaml_basics() -> None:
    """Step 1: Understanding YamlConfigSource - the simplest case."""
    console.print(Panel("Step 1: YamlConfigSource Basics", style="bold blue"))

    config_data: ConfigDict = {
        "app_name": "My App",
        "debug": True,
        "database": {"host": "localhost", "port": 5432},
    }

    console.print("🎯 Creating a simple YAML configuration:")
    print_yaml_config("Example YAML Configuration", config_data)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        yaml_path = Path(f.name)

    try:
        yaml_source = YamlConfigSource(yaml_path)
        loaded_data = yaml_source.load()

        console.print("📥 Loaded by YamlConfigSource:")
        pprint(loaded_data)

        console.print("\n💡 Key insight: YamlConfigSource.load() returns a Python dict")
        console.print("   This dict can then be used to create Pydantic models")

    finally:
        yaml_path.unlink()

    console.print()


def step_2_environment_basics() -> None:
    """Step 2: Understanding EnvironmentConfigSource - environment variables."""
    console.print(Panel("Step 2: EnvironmentConfigSource Basics", style="bold blue"))

    original_env: EnvVarsDict = dict(os.environ)

    try:
        test_env_vars: EnvVarsDict = {
            "MYAPP_NAME": "Environment App",  # Will be parsed as string
            "MYAPP_DEBUG": "false",  # Will be parsed as boolean
            "MYAPP_PORT": "8080",  # Will be parsed as integer
            "OTHER_VAR": "ignored",  # No MYAPP_ prefix, so ignored
        }

        os.environ.update(test_env_vars)

        console.print("🎯 Setting up environment variables:")
        print_env_vars("Environment Variables", test_env_vars, prefix="MYAPP_")

        env_source = EnvironmentConfigSource(prefix="MYAPP")
        loaded_data = env_source.load()

        console.print("\n📥 Loaded by EnvironmentConfigSource:")
        pprint(loaded_data)

        console.print("\n💡 Key insights:")
        console.print("   • Only variables with the prefix are loaded")
        console.print("   • The prefix is stripped from the key names")
        console.print("   • Values are automatically parsed (JSON parsing)")
        console.print("   • 'false' becomes False, '8080' becomes 8080")

    finally:
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def step_3_environment_nesting() -> None:
    """Step 3: Understanding nested structures in environment variables."""
    console.print(Panel("Step 3: Environment Nesting with Delimiters", style="bold blue"))

    original_env: EnvVarsDict = dict(os.environ)

    try:
        nested_env_vars: EnvVarsDict = {
            "APP_DATABASE__HOST": "db.example.com",
            "APP_DATABASE__PORT": "5432",
            "APP_DATABASE__CREDENTIALS__USER": "admin",
            "APP_DATABASE__CREDENTIALS__PASS": "secret",
            "APP_CACHE__REDIS__HOST": "redis.example.com",
            "APP_CACHE__REDIS__PORT": "6379",
        }

        os.environ.update(nested_env_vars)

        console.print("🎯 Setting up nested environment variables:")
        print_env_vars("Nested Environment Variables", nested_env_vars, prefix="APP_")

        # Load with default delimiter "__"
        env_source = EnvironmentConfigSource(prefix="APP", delimiter="__")
        loaded_data = env_source.load()

        console.print("\n📥 Loaded nested structure:")
        pprint(loaded_data)

        console.print("\n💡 Key insights:")
        console.print("   • '__' delimiter creates nested dictionaries")
        console.print("   • APP_DATABASE__HOST becomes {'database': {'host': ...}}")
        console.print("   • Multiple levels: APP_DATABASE__CREDENTIALS__USER")
        console.print("     becomes {'database': {'credentials': {'user': ...}}}")

    finally:
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def step_4_json_parsing() -> None:
    """Step 4: Understanding JSON parsing in environment variables."""
    console.print(Panel("Step 4: JSON Parsing in Environment Variables", style="bold blue"))

    original_env: EnvVarsDict = dict(os.environ)

    try:
        # Set environment variables with different value types
        complex_list: list[str] = ["item1", "item2", "item3"]
        complex_dict: dict[str, str | int | bool] = {"nested": True, "count": 42}

        json_env_vars: EnvVarsDict = {
            "JSON_STRING": "simple_string",
            "JSON_NUMBER": "123",
            "JSON_FLOAT": "45.67",
            "JSON_BOOLEAN": "true",
            "JSON_LIST": json.dumps(complex_list),
            "JSON_DICT": json.dumps(complex_dict),
            "JSON_INVALID": "not{valid}json",
        }

        os.environ.update(json_env_vars)

        console.print("🎯 Setting up environment variables with different data types:")

        # Create a special table for JSON parsing demo
        table = Table(
            title="🧪 JSON Parsing Test Variables",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Raw Value", style="yellow")
        table.add_column("Expected Type", style="green")

        type_mapping: dict[str, str] = {
            "JSON_STRING": "string",
            "JSON_NUMBER": "integer",
            "JSON_FLOAT": "float",
            "JSON_BOOLEAN": "boolean",
            "JSON_LIST": "list",
            "JSON_DICT": "dict",
            "JSON_INVALID": "string (fallback)",
        }

        for key, value in json_env_vars.items():
            table.add_row(key, str(value), type_mapping[key])

        console.print(table)

        env_source = EnvironmentConfigSource(prefix="JSON")
        loaded_data = env_source.load()

        console.print("\n📥 Loaded with automatic type parsing:")
        pprint(loaded_data)
        for key, value in loaded_data.items():
            console.print(f"   {key}: {value} (type: {type(value).__name__})")

        console.print("\n💡 Key insights:")
        console.print("   • EnvironmentConfigSource tries to parse values as JSON first")
        console.print("   • If JSON parsing fails, it keeps the value as a string")
        console.print("   • This allows complex data structures in environment variables")
        console.print("   • Numbers, booleans, lists, and dicts are automatically converted")

    finally:
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def step_5_composite_merging() -> None:
    """Step 5: Understanding how CompositeConfigSource merges sources."""
    console.print(Panel("Step 5: CompositeConfigSource Deep Merging", style="bold blue"))

    # Create first source (base config)
    base_config: ConfigDict = {
        "app_name": "Base App",
        "database": {"host": "localhost", "port": 5432, "pool_size": 10},
        "features": {"logging": True, "caching": False},
    }

    # Create second source (overrides)
    override_config: ConfigDict = {
        "app_name": "Override App",  # This will replace the base value
        "database": {
            "host": "production.com",  # This will replace the base value
            "ssl": True,  # This will be added
            # Note: port and pool_size are NOT specified, so base values remain
        },
        "features": {
            "caching": True,  # This will replace the base value
            "metrics": True,  # This will be added
            # Note: logging is NOT specified, so base value remains
        },
    }

    # Create temporary YAML files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        yaml.dump(base_config, f1)
        base_path = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        yaml.dump(override_config, f2)
        override_path = Path(f2.name)

    try:
        # Create sources
        base_source = YamlConfigSource(base_path)
        override_source = YamlConfigSource(override_path)

        console.print("🎯 Comparing base and override configurations:")
        print_yaml_config("Base Configuration", base_config, "defaults and structure")
        print_yaml_config("Override Configuration", override_config, "production overrides")

        # Combine sources - ORDER MATTERS!
        composite = CompositeConfigSource(base_source, override_source)
        merged_data = composite.load()

        console.print("\n📥 Merged result (base + override):")
        pprint(merged_data)

        console.print("\n💡 Key insights about deep merging:")
        console.print("   • Later sources override earlier sources")
        console.print("   • Merging is 'deep' - nested dicts are merged, not replaced")
        console.print("   • database.port (5432) and database.pool_size (10) are preserved")
        console.print("   • database.host is overridden, database.ssl is added")
        console.print("   • features.logging is preserved, features.caching is overridden")
        console.print("   • features.metrics is added")

        # Show what happens with different order
        console.print("\n🔄 What if we reverse the order?")
        reverse_composite = CompositeConfigSource(override_source, base_source)
        reverse_merged = reverse_composite.load()

        console.print("📥 Merged result (override + base):")
        pprint(reverse_merged)

        console.print("\n💡 Notice how the order changes the result!")
        console.print("   • app_name is now 'Base App' (base overrides override)")
        console.print("   • database.host is now 'localhost' (base overrides override)")

    finally:
        base_path.unlink()
        override_path.unlink()

    console.print()


def step_6_real_world_pattern() -> None:
    """Step 6: Real-world pattern - YAML + Environment."""
    console.print(Panel("Step 6: Real-World Pattern - YAML + Environment", style="bold blue"))

    # This is the most common pattern:
    # 1. YAML file with defaults and non-sensitive config
    # 2. Environment variables for secrets and runtime overrides

    yaml_config: ConfigDict = {
        "app_name": "Production App",
        "database": {
            "host": "db.production.com",
            "port": 5432,
            "name": "myapp_prod",
            "pool_size": 20,
            # Note: password is NOT in YAML (security!)
        },
        "features": {"logging": True, "metrics": True, "debug": False},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_config, f)
        yaml_path = Path(f.name)

    original_env: EnvVarsDict = dict(os.environ)

    try:
        # Set environment variables for secrets and overrides
        prod_env_vars: EnvVarsDict = {
            "PROD_DATABASE__PASSWORD": "super_secret_password",  # Secret!
            "PROD_DATABASE__PORT": "3306",  # Runtime override
            "PROD_FEATURES__DEBUG": "true",  # Runtime override
            "PROD_NEW_FEATURE": "true",  # New config
        }

        os.environ.update(prod_env_vars)

        console.print("🎯 Real-world configuration setup:")
        print_yaml_config("YAML Configuration", yaml_config, "defaults and non-sensitive config")
        print_env_vars("Environment Variables", prod_env_vars, prefix="PROD_")

        # Create sources
        yaml_source = YamlConfigSource(yaml_path)
        env_source = EnvironmentConfigSource(prefix="PROD")

        console.print("\n📥 YAML source data:")
        pprint(yaml_source.load())

        console.print("\n📥 Environment source data:")
        pprint(env_source.load())

        # Combine: YAML first (defaults), then environment (overrides)
        composite = CompositeConfigSource(yaml_source, env_source)
        final_config = composite.load()

        console.print("\n🎯 Final merged configuration:")
        pprint(final_config)

        console.print("\n💡 Real-world insights:")
        console.print("   • YAML provides structured defaults and non-sensitive config")
        console.print("   • Environment variables provide secrets and runtime overrides")
        console.print("   • Secrets never appear in version-controlled YAML files")
        console.print("   • Environment can override any YAML value")
        console.print("   • Environment can add new configuration not in YAML")
        console.print("   • This pattern works great with Docker, Kubernetes, etc.")

    finally:
        yaml_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def step_7_integration_with_pydantic() -> None:
    """Step 7: How this integrates with Pydantic models."""
    console.print(Panel("Step 7: Integration with Pydantic Models", style="bold blue"))

    from pydantic import BaseModel
    from pydantic_settings import BaseSettings, SettingsConfigDict

    from frostbound.pydanticonf.loader import ConfigLoader

    # Define your data models
    class DatabaseConfig(BaseModel):
        host: str
        port: int
        name: str
        password: str
        pool_size: int = 10

    class FeaturesConfig(BaseModel):
        logging: bool = True
        metrics: bool = False
        debug: bool = False

    class AppSettings(BaseSettings):
        app_name: str
        database: DatabaseConfig
        features: FeaturesConfig

        model_config = SettingsConfigDict(case_sensitive=False)

    # Create configuration data
    yaml_config: ConfigDict = {
        "app_name": "Pydantic Demo",
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "demo_db",
            "password": "yaml_password",
            "pool_size": 15,
        },
        "features": {"logging": True, "metrics": False},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_config, f)
        yaml_path = Path(f.name)

    original_env: EnvVarsDict = dict(os.environ)

    try:
        # Override some values with environment
        demo_env_vars: EnvVarsDict = {
            "DEMO_DATABASE__PASSWORD": "env_secret_password",
            "DEMO_FEATURES__DEBUG": "true",
        }

        os.environ.update(demo_env_vars)

        console.print("🎯 Pydantic integration example:")
        print_yaml_config("YAML Configuration", yaml_config, "base configuration")
        print_env_vars("Environment Overrides", demo_env_vars, prefix="DEMO_")

        # Method 1: Manual source creation
        yaml_source = YamlConfigSource(yaml_path)
        env_source = EnvironmentConfigSource(prefix="DEMO")

        settings = ConfigLoader.from_sources(AppSettings, yaml_source, env_source)  # type: ignore[attr-defined]

        console.print("\n🎯 Parsed Pydantic settings object:")
        pprint(settings)
        console.print(f"   Type: {type(settings)}")
        console.print(f"   app_name: {settings.app_name}")
        console.print(f"   database.host: {settings.database.host}")
        console.print(f"   database.password: {settings.database.password}")
        console.print(f"   features.debug: {settings.features.debug}")

        # Method 2: Convenient helper method
        settings2 = ConfigLoader.from_yaml_with_env(AppSettings, yaml_path=yaml_path, env_prefix="DEMO")  # type: ignore[attr-defined]
        pprint(settings2)

        console.print("\n✅ Both methods produce the same result:")
        console.print(f"   settings == settings2: {settings == settings2}")

        console.print("\n💡 Pydantic integration insights:")
        console.print("   • ConfigLoader.from_sources() takes any number of sources")
        console.print("   • Sources are merged, then passed to Pydantic for validation")
        console.print("   • Pydantic validates types, applies defaults, etc.")
        console.print("   • You get type-safe, validated configuration objects")
        console.print("   • ConfigLoader provides convenient helper methods")

    finally:
        yaml_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def main() -> None:
    """Run all learning steps."""
    console.print(
        Panel.fit(
            "🎓 Step-by-Step Learning Guide\n"
            "frostbound.pydanticonf.sources\n\n"
            "This guide will walk you through each concept\n"
            "to build your intuition about how configuration\n"
            "loading works in this library.",
            title="Learning Guide",
            style="bold green",
        )
    )

    # step_1_yaml_basics()
    # step_2_environment_basics()
    # step_3_environment_nesting()
    # step_4_json_parsing()
    # step_5_composite_merging()
    # step_6_real_world_pattern()
    step_7_integration_with_pydantic()

    console.print(
        Panel.fit(
            "🎉 Congratulations!\n\n"
            "You now understand the core concepts:\n\n"
            "1. YamlConfigSource loads structured data from YAML\n"
            "2. EnvironmentConfigSource loads from env vars with smart parsing\n"
            "3. CompositeConfigSource merges sources with deep merging\n"
            "4. ConfigLoader integrates everything with Pydantic\n\n"
            "The typical pattern is:\n"
            "YAML (defaults) + Environment (secrets/overrides) → Pydantic (validation)",
            title="🎓 Learning Complete!",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()
