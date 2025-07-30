"""Example usage of the dependency injection container."""

from typing import Any, Dict, Protocol, final, runtime_checkable

from frostbound.di import Container, Scope, get_container

# Example 1: Basic dependency injection
# -------------------------------------------


# Define some interfaces
@runtime_checkable
class ILogger(Protocol):
    """Protocol for a logger."""

    def log(self, message: str) -> None:
        """Log a message."""
        ...


@runtime_checkable
class IUserRepository(Protocol):
    """Protocol for a user repository."""

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID."""
        ...


# Define implementations
@final
class ConsoleLogger:
    """A simple console logger."""

    def __init__(self) -> None:
        """Initialize the logger."""
        pass

    def log(self, message: str) -> None:
        """Log a message to the console."""
        print(f"[LOG] {message}")


@final
class PostgresUserRepository:
    """A user repository that uses Postgres."""

    def __init__(self, logger: ConsoleLogger) -> None:
        """Initialize with a logger.

        Args:
            logger: The logger to use
        """
        self.logger = logger

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            The user
        """
        self.logger.log(f"Getting user with ID {user_id}")
        # In a real app, this would query the database
        return {"id": user_id, "name": "John Doe"}


@final
class UserService:
    """A service for managing users."""

    def __init__(self, repo: PostgresUserRepository, logger: ConsoleLogger) -> None:
        """Initialize with a repository and logger.

        Args:
            repo: The user repository to use
            logger: The logger to use
        """
        self.repo = repo
        self.logger = logger

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            The user
        """
        self.logger.log(f"UserService: Getting user with ID {user_id}")
        return self.repo.get_user_by_id(user_id)


def example_basic_usage() -> None:
    """Example of basic usage."""
    # Create a container
    container = Container()

    # Register concrete implementations
    container.register(ConsoleLogger)

    # For classes with dependencies, we can use auto-injection
    container.register(PostgresUserRepository)

    # Register service
    container.register(UserService)

    # Resolve service and use it
    user_service = container.resolve(UserService)
    user = user_service.get_user_by_id(1)

    print(f"Found user: {user}")


# Example 2: Different scopes
# -------------------------------------------


class CounterSingleton:
    """A counter with singleton scope."""

    def __init__(self) -> None:
        """Initialize the counter."""
        self.count = 0

    def increment(self) -> int:
        """Increment the counter.

        Returns:
            The new count
        """
        self.count += 1
        return self.count


class CounterTransient:
    """A counter with transient scope."""

    def __init__(self) -> None:
        """Initialize the counter."""
        self.count = 0

    def increment(self) -> int:
        """Increment the counter.

        Returns:
            The new count
        """
        self.count += 1
        return self.count


class CounterScoped:
    """A counter with scoped lifetime."""

    def __init__(self) -> None:
        """Initialize the counter."""
        self.count = 0

    def increment(self) -> int:
        """Increment the counter.

        Returns:
            The new count
        """
        self.count += 1
        return self.count


def example_scopes() -> None:
    """Example of different scopes."""
    # Create a container
    container = Container()

    # Register with different scopes
    container.register(CounterSingleton, scope=Scope.SINGLETON)
    container.register(CounterTransient, scope=Scope.TRANSIENT)
    container.register(CounterScoped, scope=Scope.SCOPED)

    # Singleton: should be the same instance
    singleton1 = container.resolve(CounterSingleton)
    singleton2 = container.resolve(CounterSingleton)
    print(f"Singleton 1 increment: {singleton1.increment()}")  # 1
    print(f"Singleton 2 increment: {singleton2.increment()}")  # 2 (same instance)

    # Transient: should be different instances
    transient1 = container.resolve(CounterTransient)
    transient2 = container.resolve(CounterTransient)
    print(f"Transient 1 increment: {transient1.increment()}")  # 1
    print(f"Transient 2 increment: {transient2.increment()}")  # 1 (different instance)

    # Scoped: should be the same instance within the same thread
    scoped1 = container.resolve(CounterScoped)
    scoped2 = container.resolve(CounterScoped)
    print(f"Scoped 1 increment: {scoped1.increment()}")  # 1
    print(f"Scoped 2 increment: {scoped2.increment()}")  # 2 (same instance in same thread)

    # If we clear the scope, we should get a new instance
    provider = container._providers[CounterScoped]
    if hasattr(provider, "clear_scope"):
        provider.clear_scope()

    scoped3 = container.resolve(CounterScoped)
    print(f"Scoped 3 increment after clearing: {scoped3.increment()}")  # 1 (new instance)


# Example 3: Factory registration
# -------------------------------------------


class ConfigService:
    """A service for accessing configuration."""

    def __init__(self, config_path: str) -> None:
        """Initialize with a config path.

        Args:
            config_path: The path to the config file
        """
        self.config_path = config_path

    def get_config(self) -> Dict[str, str]:
        """Get the configuration.

        Returns:
            The configuration
        """
        # In a real app, this would load from the file
        return {"database_url": "postgresql://localhost/mydb"}


def create_config_service() -> ConfigService:
    """Create a config service.

    Returns:
        The config service
    """
    return ConfigService("config.json")


def example_factory() -> None:
    """Example of factory registration."""
    # Create a container
    container = Container()

    # Register with a factory
    container.register_factory(ConfigService, create_config_service)

    # Resolve the service
    config_service = container.resolve(ConfigService)
    config = config_service.get_config()

    print(f"Config: {config}")


# Example 4: Singleton container
# -------------------------------------------


def example_singleton_container() -> None:
    """Example of using the singleton container."""
    # Get the singleton container
    container1 = get_container()
    container2 = get_container()

    print(f"Same container? {container1 is container2}")  # True

    # Register a service in one container
    container1.register(ConsoleLogger)

    # Resolve from the other container
    resolved_logger = container2.resolve(ConsoleLogger)
    resolved_logger.log("This message should appear")


if __name__ == "__main__":
    print("\n--- Example 1: Basic Usage ---")
    example_basic_usage()

    print("\n--- Example 2: Different Scopes ---")
    example_scopes()

    print("\n--- Example 3: Factory Registration ---")
    example_factory()

    print("\n--- Example 4: Singleton Container ---")
    example_singleton_container()
