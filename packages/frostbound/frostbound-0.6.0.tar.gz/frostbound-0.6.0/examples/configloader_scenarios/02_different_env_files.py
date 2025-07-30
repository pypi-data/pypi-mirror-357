"""
Example 02: Different Environment File Names
Demonstrates loading from different environment files like .env.dev, .env.prod
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.table import Table

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_different_env_files():
    """Show loading from different env file names."""
    console.print(Panel("Example 02: Different Environment File Names", style="bold blue"))

    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Check which env files exist
    console.print("\n[bold]Available env files:[/bold]")
    console.print(f"[dim]Looking in: {script_dir}[/dim]")
    for env_file in [".env", ".env.dev", ".env.prod"]:
        file_path = script_dir / env_file
        exists = file_path.exists()
        console.print(f"  {env_file}: {'[green]✓ exists[/green]' if exists else '[red]✗ missing[/red]'}")

    if not all((script_dir / f).exists() for f in [".env", ".env.dev", ".env.prod"]):
        console.print("\n[red]⚠️  Some env files are missing![/red]")
        console.print(
            "[yellow]Make sure you're running this from the examples/configloader_scenarios directory[/yellow]"
        )

    # Base settings class
    class Settings(BaseSettings):
        app_name: str = "DefaultApp"
        debug: bool = False
        port: int = 3000
        database_url: str = "sqlite:///default.db"
        secret_key: str = "not-set"
        log_level: str = "WARNING"
        cache_enabled: bool = False
        rate_limit: int = 500
        ssl_enabled: bool = False
        workers: int = 1

    # Create table to compare environments
    table = Table(title="Environment Configurations Comparison")
    table.add_column("Setting", style="cyan")
    table.add_column(".env (default)", style="green")
    table.add_column(".env.dev", style="yellow")
    table.add_column(".env.prod", style="red")

    # Load from different env files with absolute paths
    class DefaultSettings(Settings):
        model_config = SettingsConfigDict(env_file=str(script_dir / ".env"))

    class DevSettings(Settings):
        model_config = SettingsConfigDict(env_file=str(script_dir / ".env.dev"))

    class ProdSettings(Settings):
        model_config = SettingsConfigDict(env_file=str(script_dir / ".env.prod"))

    console.print("\n[bold]Loading settings with Pydantic directly:[/bold]")

    default = DefaultSettings()
    console.print("\n[green]DefaultSettings (from .env):[/green]")
    console.print(f"  Loaded from: {DefaultSettings.model_config.get('env_file', 'Not set')}")
    pprint(default)

    dev = DevSettings()
    console.print("\n[yellow]DevSettings (from .env.dev):[/yellow]")
    console.print(f"  Loaded from: {DevSettings.model_config.get('env_file', 'Not set')}")
    pprint(dev)

    prod = ProdSettings()
    console.print("\n[red]ProdSettings (from .env.prod):[/red]")
    console.print(f"  Loaded from: {ProdSettings.model_config.get('env_file', 'Not set')}")
    pprint(prod)

    # Add rows to table
    table.add_row("App Name", default.app_name, dev.app_name, prod.app_name)
    table.add_row("Debug", str(default.debug), str(dev.debug), str(prod.debug))
    table.add_row("Port", str(default.port), str(dev.port), str(prod.port))
    table.add_row("Log Level", default.log_level, dev.log_level, prod.log_level)
    table.add_row("Cache Enabled", str(default.cache_enabled), str(dev.cache_enabled), str(prod.cache_enabled))
    table.add_row("Rate Limit", str(default.rate_limit), str(dev.rate_limit), str(prod.rate_limit))
    table.add_row("SSL Enabled", str(default.ssl_enabled), str(dev.ssl_enabled), str(prod.ssl_enabled))
    table.add_row("Workers", str(default.workers), str(dev.workers), str(prod.workers))

    console.print("\n")
    console.print(table)

    # Demonstrate ConfigLoader with different env files
    console.print("\n[bold]Using ConfigLoader with different env files:[/bold]")

    # Method 1: ConfigLoader respects env_file configuration
    console.print("\n[yellow]Method 1: ConfigLoader detects and respects env_file:[/yellow]")

    default_settings_via_loader = ConfigLoader.from_yaml_with_env(DefaultSettings)
    pprint(default_settings_via_loader)
    assert default == default_settings_via_loader
    console.print(
        f"  Default via ConfigLoader: {default_settings_via_loader.app_name} (port: {default_settings_via_loader.port})"
    )

    # ConfigLoader with dev settings
    dev_settings_via_loader = ConfigLoader.from_yaml_with_env(DevSettings)
    pprint(dev_settings_via_loader)
    assert dev == dev_settings_via_loader
    console.print(f"  Dev via ConfigLoader: {dev_settings_via_loader.app_name} (port: {dev_settings_via_loader.port})")

    # ConfigLoader with prod settings
    prod_settings_via_loader = ConfigLoader.from_yaml_with_env(ProdSettings)
    pprint(prod_settings_via_loader)
    assert prod == prod_settings_via_loader
    console.print(
        f"  Prod via ConfigLoader: {prod_settings_via_loader.app_name} (port: {prod_settings_via_loader.port})"
    )

    console.print("\n[dim]→ ConfigLoader automatically detects the env_file config and uses it![/dim]")

    # Method 2: Adding YAML override on top of different env files
    console.print("\n[yellow]Method 2: Adding YAML override to different env files:[/yellow]")

    # Create a temporary YAML for override demo
    override_yaml_path = script_dir / "override.yaml"
    with open(override_yaml_path, "w") as f:
        f.write("log_level: CRITICAL\n")
        f.write("cache_enabled: true\n")

    try:
        dev_with_yaml = ConfigLoader.from_yaml_with_env(DevSettings, yaml_path=override_yaml_path)
        pprint(dev_with_yaml)
        prod_with_yaml = ConfigLoader.from_yaml_with_env(ProdSettings, yaml_path=override_yaml_path)
        pprint(prod_with_yaml)

        console.print(f"  Dev + YAML: log_level={dev_with_yaml.log_level} (was DEBUG)")
        console.print(f"  Prod + YAML: log_level={prod_with_yaml.log_level} (was WARNING)")
        console.print(f"  Both now have cache_enabled={dev_with_yaml.cache_enabled}")

    finally:
        if override_yaml_path.exists():
            override_yaml_path.unlink()

    # Demonstrate using environment variable to select env file
    console.print("\n[bold]Dynamic environment selection:[/bold]")
    console.print("[dim]You can use environment variables to select which .env file to load:[/dim]")
    console.print("""
    import os
    env = os.getenv("ENVIRONMENT", "dev")

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=f".env.{env}"  # Loads .env.dev, .env.prod, etc.
        )

    # Works with ConfigLoader too!
    settings = ConfigLoader.from_yaml_with_env(Settings, yaml_path=Path("config.yaml"))
    """)


if __name__ == "__main__":
    demo_different_env_files()
