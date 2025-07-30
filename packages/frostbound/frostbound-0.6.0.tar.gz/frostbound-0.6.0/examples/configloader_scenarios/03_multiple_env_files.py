"""
Example 03: Multiple Environment Files
Demonstrates loading from multiple .env files with precedence
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

console = Console()


def demo_multiple_env_files():
    """Show loading from multiple env files with precedence."""
    console.print(Panel("Example 03: Multiple Environment Files", style="bold blue"))

    # First, create a .env.shared file with common settings
    with open(".env.shared", "w") as f:
        f.write("# Shared settings across all environments\n")
        f.write("APP_VERSION=1.0.0\n")
        f.write("TIMEZONE=UTC\n")
        f.write("DEFAULT_LANGUAGE=en\n")
        f.write("PORT=3000\n")  # This will be overridden

    try:
        # Load from multiple env files - later files override earlier ones
        class Settings(BaseSettings):
            model_config = SettingsConfigDict(
                env_file=[".env.shared", ".env"],  # List of files in precedence order
                env_prefix="",
            )

            # Settings from .env.shared
            app_version: str = "0.0.0"
            timezone: str = "America/New_York"
            default_language: str = "en-US"

            # Settings from .env (will override .env.shared)
            app_name: str = "DefaultApp"
            port: int = 8000
            debug: bool = False
            database_url: str = "sqlite:///default.db"

        settings = Settings()

        console.print("\n[bold]Settings loaded from multiple files:[/bold]")
        console.print("[dim](.env.shared values are overridden by .env)[/dim]\n")

        console.print("[yellow]From .env.shared:[/yellow]")
        console.print(f"  App Version: [green]{settings.app_version}[/green]")
        console.print(f"  Timezone: [green]{settings.timezone}[/green]")
        console.print(f"  Default Language: [green]{settings.default_language}[/green]")

        console.print("\n[yellow]From .env (overrides):[/yellow]")
        console.print(f"  App Name: [green]{settings.app_name}[/green]")
        console.print(f"  Port: [green]{settings.port}[/green] (overrode .env.shared)")
        console.print(f"  Debug: [green]{settings.debug}[/green]")
        console.print(f"  Database URL: [green]{settings.database_url}[/green]")

        # Demonstrate with environment-specific layering
        console.print("\n[bold]Environment-specific layering example:[/bold]")

        class ProdSettings(BaseSettings):
            model_config = SettingsConfigDict(
                env_file=[".env.shared", ".env", ".env.prod"],  # Layered configuration
                env_prefix="",
            )

            app_version: str = "0.0.0"
            app_name: str = "DefaultApp"
            port: int = 8000
            debug: bool = True
            ssl_enabled: bool = False
            workers: int = 1

        prod_settings = ProdSettings()

        console.print("\n[dim]Loading order: .env.shared → .env → .env.prod[/dim]")
        console.print(f"  App Name: [green]{prod_settings.app_name}[/green] (from .env.prod)")
        console.print(f"  Port: [green]{prod_settings.port}[/green] (from .env.prod)")
        console.print(f"  Debug: [green]{prod_settings.debug}[/green] (from .env.prod)")
        console.print(f"  SSL Enabled: [green]{prod_settings.ssl_enabled}[/green] (from .env.prod)")
        console.print(f"  Workers: [green]{prod_settings.workers}[/green] (from .env.prod)")
        console.print(f"  App Version: [green]{prod_settings.app_version}[/green] (from .env.shared)")

    finally:
        import os

        if os.path.exists(".env.shared"):
            os.unlink(".env.shared")


if __name__ == "__main__":
    demo_multiple_env_files()
