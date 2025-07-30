"""
Test and Demonstration: _merge_config_data Function

This script demonstrates what _merge_config_data is for and why it's important
in the hybrid approach. It shows the difference between shallow and deep merging
when combining configuration data.
"""

import sys
import tempfile
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf import ConfigLoader

console = Console()


def test_deep_merge_necessity():
    """Demonstrate why _merge_config_data is necessary for proper nested config handling."""
    console.print("🔍 [bold]Why _merge_config_data is Necessary[/bold]")

    # Create .env file with simple config
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("APP_SECRET=env_secret\n")
        f.write("APP_DEBUG=true\n")
        f.write("APP_PORT=8080\n")
        env_file = f.name

    # Create YAML file with nested database config that should be merged
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
database:
  host: "yaml_db_host"
  port: 3306
  pool_size: 20

cache:
  host: "yaml_cache_host"
  timeout: 30

port: 9000  # Override port from .env
log_level: "DEBUG"  # New field
""")
        yaml_file = f.name

    try:
        # Settings with mixed flat and nested configuration
        class Settings(BaseSettings):
            model_config = SettingsConfigDict(env_file=env_file, env_prefix="APP_", extra="allow")

            secret: str = "default_secret"
            debug: bool = False
            port: int = 3000
            log_level: str = "INFO"

        # Load using hybrid approach
        settings = ConfigLoader.from_yaml_with_env(Settings, Path(yaml_file))

        console.print("   [bold]Results with Deep Merging:[/bold]")
        console.print(f"     Secret: [green]{settings.secret}[/green] (from .env)")
        console.print(f"     Debug: [green]{settings.debug}[/green] (from .env)")
        console.print(f"     Port: [green]{settings.port}[/green] (YAML overrides .env)")
        console.print(f"     Log Level: [green]{settings.log_level}[/green] (YAML addition)")

        # Check if nested database config was added
        if hasattr(settings, "database"):
            console.print(f"     Database: [green]{settings.database}[/green] (YAML addition)")

        # Verify deep merging worked correctly
        assert settings.secret == "env_secret", "Should keep secret from .env"
        assert settings.debug, "Should keep debug from .env"
        assert settings.port == 9000, "YAML should override port"
        assert settings.log_level == "DEBUG", "Should add log_level from YAML"

        console.print("\n   ✅ [green]Deep merging preserves .env values while adding YAML![/green]")
        console.print("     [yellow]_merge_config_data ensures no data loss during override[/yellow]")

    finally:
        import os

        os.unlink(env_file)
        os.unlink(yaml_file)


def test_shallow_vs_deep_merge():
    """Demonstrate the difference between shallow and deep merging."""
    console.print("\n🔄 [bold]Shallow vs Deep Merge Comparison[/bold]")

    # Example data structures
    base_data = {
        "database": {"host": "env_host", "port": 5433, "password": "env_secret"},
        "cache": {"host": "env_cache", "ttl": 3600},
        "debug": True,
    }

    override_data = {"database": {"host": "yaml_host", "pool_size": 20}, "cache": {"timeout": 30}, "log_level": "DEBUG"}

    # Shallow merge (what would happen without _merge_config_data)
    shallow_result = base_data.copy()
    shallow_result.update(override_data)

    # Deep merge (what _merge_config_data does)
    deep_result = ConfigLoader._merge_config_data(base_data, override_data)

    console.print("   [bold]Base data:[/bold]")
    pprint(base_data, console=console)

    console.print("\n   [bold]Override data:[/bold]")
    pprint(override_data, console=console)

    console.print("\n   [bold]Shallow merge result (BAD):[/bold]")
    pprint(shallow_result, console=console)
    console.print("     [red]❌ Lost env_secret password and env_cache host![/red]")

    console.print("\n   [bold]Deep merge result (GOOD):[/bold]")
    pprint(deep_result, console=console)
    console.print("     [green]✅ Preserved all values while adding new ones![/green]")

    # Verify deep merge preserves nested values
    assert deep_result["database"]["password"] == "env_secret", "Should preserve password"
    assert deep_result["database"]["port"] == 5433, "Should preserve port"
    assert deep_result["database"]["host"] == "yaml_host", "Should override host"
    assert deep_result["database"]["pool_size"] == 20, "Should add pool_size"
    assert deep_result["cache"]["host"] == "env_cache", "Should preserve cache host"
    assert deep_result["cache"]["ttl"] == 3600, "Should preserve cache ttl"
    assert deep_result["cache"]["timeout"] == 30, "Should add cache timeout"


def main():
    """Run tests to demonstrate _merge_config_data functionality."""
    console.print(
        Panel.fit(
            "🔧 _merge_config_data Function Demonstration\n\n"
            "This shows why _merge_config_data is essential for the\n"
            "hybrid approach. It enables proper deep merging of\n"
            "nested configuration data, preserving values from\n"
            "both .env files and YAML overrides.\n\n"
            "Without it, nested configs would be completely replaced!",
            title="Deep Merge Demo",
            style="bold cyan",
        )
    )

    try:
        test_deep_merge_necessity()
        test_shallow_vs_deep_merge()

        console.print(
            Panel.fit(
                "🎉 _merge_config_data Purpose Demonstrated!\n\n"
                "Key insights:\n\n"
                "✅ _merge_config_data enables proper nested config handling\n"
                "✅ Deep merging preserves values from both sources\n"
                "✅ Shallow merging would lose nested configuration data\n"
                "✅ Essential for Pydantic-native mode YAML overrides\n\n"
                "This function is crucial for the hybrid approach to work\n"
                "correctly with complex, nested configurations!",
                title="🧠 Understanding Complete",
                style="bold green",
            )
        )

        return 0

    except Exception as e:
        console.print(f"\n❌ [bold red]TEST FAILED: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
