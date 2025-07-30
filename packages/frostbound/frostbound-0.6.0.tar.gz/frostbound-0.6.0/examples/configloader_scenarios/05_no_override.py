"""
Example 05: No Override Scenarios
Demonstrates loading with only one source (no overrides)
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_no_override():
    """Show loading from single sources without overrides."""
    console.print(Panel("Example 05: No Override Scenarios", style="bold blue"))

    # Base settings class
    class Settings(BaseSettings):
        app_name: str = "DefaultApp"
        debug: bool = False
        port: int = 3000
        database_url: str = "sqlite:///default.db"
        log_level: str = "WARNING"
        cache_enabled: bool = False

    # 1. Only defaults (no env file, no YAML)
    console.print("\n[bold]1. Only defaults (no external config):[/bold]")
    settings_defaults = Settings(_env_file=None)  # Explicitly disable env file
    console.print(f"  App Name: [yellow]{settings_defaults.app_name}[/yellow]")
    console.print(f"  Debug: [yellow]{settings_defaults.debug}[/yellow]")
    console.print(f"  Port: [yellow]{settings_defaults.port}[/yellow]")
    console.print("[dim]  (All values are from class defaults)[/dim]")

    # 2. Only .env file (no YAML)
    console.print("\n[bold]2. Only .env file (no YAML):[/bold]")

    class EnvOnlySettings(Settings):
        model_config = SettingsConfigDict(env_file=".env")

    settings_env_only = EnvOnlySettings()
    console.print(f"  App Name: [green]{settings_env_only.app_name}[/green]")
    console.print(f"  Debug: [green]{settings_env_only.debug}[/green]")
    console.print(f"  Port: [green]{settings_env_only.port}[/green]")
    console.print("[dim]  (Values from .env file)[/dim]")

    # 3. Only YAML (no .env)
    console.print("\n[bold]3. Only YAML (no .env):[/bold]")
    settings_yaml_only = ConfigLoader.from_yaml(Settings, Path("config.yaml"))
    console.print(f"  App Name: [blue]{settings_yaml_only.app_name}[/blue]")
    console.print(f"  Port: [blue]{settings_yaml_only.port}[/blue]")
    console.print("[dim]  (Values from config.yaml)[/dim]")

    # 4. Only environment variables (no files)
    console.print("\n[bold]4. Only environment variables (no files):[/bold]")
    import os

    # Set some environment variables
    os.environ["MY_APP_NAME"] = "EnvVarApp"
    os.environ["MY_DEBUG"] = "false"
    os.environ["MY_PORT"] = "5000"

    try:
        settings_env_vars = ConfigLoader.from_env(Settings, env_prefix="MY_")
        console.print(f"  App Name: [magenta]{settings_env_vars.app_name}[/magenta]")
        console.print(f"  Debug: [magenta]{settings_env_vars.debug}[/magenta]")
        console.print(f"  Port: [magenta]{settings_env_vars.port}[/magenta]")
        console.print("[dim]  (Values from MY_* environment variables)[/dim]")
    finally:
        # Clean up environment variables
        for key in ["MY_APP_NAME", "MY_DEBUG", "MY_PORT"]:
            os.environ.pop(key, None)

    # 5. Missing YAML file scenario
    console.print("\n[bold]5. Missing YAML file (graceful handling):[/bold]")
    settings_missing_yaml = ConfigLoader.from_yaml_with_env(
        Settings,
        yaml_path=Path("non_existent.yaml"),  # This file doesn't exist
    )
    console.print(f"  App Name: [green]{settings_missing_yaml.app_name}[/green]")
    console.print(f"  Port: [green]{settings_missing_yaml.port}[/green]")
    console.print("[dim]  (Falls back to .env file when YAML is missing)[/dim]")


if __name__ == "__main__":
    demo_no_override()
