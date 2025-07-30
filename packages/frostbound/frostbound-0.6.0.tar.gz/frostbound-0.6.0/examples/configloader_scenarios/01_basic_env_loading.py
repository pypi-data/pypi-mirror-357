"""
Example 01: Basic .env File Loading
Demonstrates the simplest case of loading configuration from a .env file
using Pydantic's native env_file support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_basic_env_loading():
    """Show basic .env file loading with Pydantic's native support."""
    console.print(Panel("Example 01: Basic .env File Loading", style="bold blue"))

    # Define settings with env_file configuration
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",  # Uses the real .env file in this directory
            env_prefix="",  # No prefix for basic example
        )

        app_name: str = "DefaultApp"
        debug: bool = False
        port: int = 3000
        database_url: str = "sqlite:///default.db"
        secret_key: str = "not-set"
        log_level: str = "WARNING"

    # Load settings - Pydantic handles the .env file
    settings = Settings()
    pprint(settings)

    console.print("\n[bold]Settings loaded from .env:[/bold]")
    console.print(f"  App Name: [green]{settings.app_name}[/green]")
    console.print(f"  Debug: [green]{settings.debug}[/green]")
    console.print(f"  Port: [green]{settings.port}[/green]")
    console.print(f"  Database URL: [green]{settings.database_url}[/green]")
    console.print(f"  Secret Key: [green]{settings.secret_key[:10]}...[/green]")
    console.print(f"  Log Level: [green]{settings.log_level}[/green]")

    # Now demonstrate with ConfigLoader (hybrid mode will detect env_file)
    console.print("\n[bold]Same result using ConfigLoader.from_yaml_with_env:[/bold]")
    settings2 = ConfigLoader.from_yaml_with_env(Settings)
    pprint(settings2)
    console.print(f"  App Name: [green]{settings2.app_name}[/green]")
    console.print(f"  Debug: [green]{settings2.debug}[/green]")
    console.print(f"  Port: [green]{settings2.port}[/green]")

    console.print("\n[dim]Note: ConfigLoader detects the env_file config and respects it![/dim]")


if __name__ == "__main__":
    demo_basic_env_loading()
