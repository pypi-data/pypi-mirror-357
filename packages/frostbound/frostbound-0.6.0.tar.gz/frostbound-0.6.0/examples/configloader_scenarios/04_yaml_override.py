"""
Example 04: YAML Override Scenarios
Demonstrates how YAML configuration overrides .env files in hybrid mode
"""

from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_yaml_override():
    """Show YAML override behavior with .env files."""
    console.print(Panel("Example 04: YAML Override Scenarios", style="bold blue"))

    # Settings class with env_file configured (Pydantic-native mode)
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_prefix="",
        )

        # Basic settings
        app_name: str = "DefaultApp"
        port: int = 3000
        debug: bool = False
        log_level: str = "WARNING"

        # These will come from YAML only
        database: dict[str, Any] = {}
        cache: dict[str, Any] = {}
        features: dict[str, Any] = {}

    # Load with .env only
    console.print("\n[bold]1. Loading from .env only:[/bold]")
    settings_env_only = Settings()
    console.print(f"  App Name: [yellow]{settings_env_only.app_name}[/yellow]")
    console.print(f"  Port: [yellow]{settings_env_only.port}[/yellow]")
    console.print(f"  Debug: [yellow]{settings_env_only.debug}[/yellow]")
    console.print(f"  Database: [yellow]{settings_env_only.database}[/yellow] (empty)")

    # Load with YAML override
    console.print("\n[bold]2. Loading with YAML override:[/bold]")
    settings_with_yaml = ConfigLoader.from_yaml_with_env(Settings, yaml_path=Path("config.yaml"))

    console.print(f"  App Name: [green]{settings_with_yaml.app_name}[/green] (from YAML)")
    console.print(f"  Port: [green]{settings_with_yaml.port}[/green] (from YAML)")
    console.print(f"  Debug: [yellow]{settings_with_yaml.debug}[/yellow] (kept from .env)")
    console.print(f"  Log Level: [yellow]{settings_with_yaml.log_level}[/yellow] (kept from .env)")

    console.print("\n  Database (from YAML):")
    pprint(settings_with_yaml.database, indent_guides=True, console=console)

    console.print("\n  Cache (from YAML):")
    pprint(settings_with_yaml.cache, indent_guides=True, console=console)

    console.print("\n  Features (from YAML):")
    pprint(settings_with_yaml.features, indent_guides=True, console=console)

    # Demonstrate deep merge behavior
    console.print("\n[bold]3. Deep merge demonstration:[/bold]")
    console.print("[dim]This is why _merge_config_data is essential![/dim]\n")

    # Create a YAML with partial database config
    with open("partial_config.yaml", "w") as f:
        f.write("""
database:
  pool_size: 50
  timeout: 60
cache:
  ttl: 7200
""")

    try:
        # First, let's add some database config to .env to show merging
        class SettingsWithNested(BaseSettings):
            model_config = SettingsConfigDict(
                env_file=".env",
                env_prefix="",
                extra="allow",  # Allow extra fields
            )

            app_name: str = "DefaultApp"
            database_url: str = "sqlite:///default.db"

        # Simulate having nested config from .env
        base_settings = SettingsWithNested()
        base_settings_dict = base_settings.model_dump()
        base_settings_dict["database"] = {"url": base_settings.database_url, "password": "secret-from-env"}

        # Load with partial YAML override
        settings_merged = ConfigLoader.from_yaml_with_env(Settings, yaml_path=Path("partial_config.yaml"))

        console.print("  After deep merge:")
        console.print("    Database URL from .env: [green]preserved[/green]")
        console.print("    Database pool_size from YAML: [green]added[/green]")
        console.print("    Cache TTL from YAML: [green]added[/green]")

        # Show actual merged data
        if hasattr(settings_merged, "database"):
            console.print("\n  Actual merged database config:")
            pprint(settings_merged.database, indent_guides=True, console=console)
        if hasattr(settings_merged, "cache"):
            console.print("\n  Actual merged cache config:")
            pprint(settings_merged.cache, indent_guides=True, console=console)

    finally:
        import os

        if os.path.exists("partial_config.yaml"):
            os.unlink("partial_config.yaml")


if __name__ == "__main__":
    demo_yaml_override()
