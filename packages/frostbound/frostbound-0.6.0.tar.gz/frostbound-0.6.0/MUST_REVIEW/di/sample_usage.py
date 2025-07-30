"""Sample usage of the enterprise-grade dependency injection container.

This module demonstrates how to use the refactored DI container
in various scenarios, showcasing its flexibility and power.
"""

from typing import Protocol
from dataclasses import dataclass
from contextlib import contextmanager

from frostbound.di import Container, ContainerBuilder, Dependency, Scope, ScopeContext, inject


# Define interfaces using Protocol
class IDatabase(Protocol):
    """Database interface."""

    def execute(self, query: str) -> None:
        """Execute a database query."""
        ...

    def close(self) -> None:
        """Close the database connection."""
        ...


class ILogger(Protocol):
    """Logger interface."""

    def info(self, message: str) -> None:
        """Log an info message."""
        ...

    def error(self, message: str, exception: Exception | None = None) -> None:
        """Log an error message."""
        ...


class IUserRepository(Protocol):
    """User repository interface."""

    def get_user(self, user_id: int) -> dict:
        """Get a user by ID."""
        ...

    def save_user(self, user: dict) -> None:
        """Save a user."""
        ...


# Implementation classes
class Database:
    """Example database implementation."""

    def __init__(self, connection_string: str):
        """Initialize the database.

        Args:
            connection_string: The database connection string
        """
        self.connection_string = connection_string
        print(f"Connecting to database: {connection_string}")

    def execute(self, query: str) -> None:
        """Execute a database query.

        Args:
            query: The query to execute
        """
        print(f"Executing query: {query}")

    def close(self) -> None:
        """Close the database connection."""
        print(f"Closing database connection: {self.connection_string}")


class Logger:
    """Example logger implementation."""

    def info(self, message: str) -> None:
        """Log an info message.

        Args:
            message: The message to log
        """
        print(f"INFO: {message}")

    def error(self, message: str, exception: Exception | None = None) -> None:
        """Log an error message.

        Args:
            message: The message to log
            exception: The exception to log
        """
        if exception:
            print(f"ERROR: {message} - {str(exception)}")
        else:
            print(f"ERROR: {message}")


class UserRepository:
    """Example user repository implementation."""

    # Demonstrates declarative dependency injection
    db = Dependency[IDatabase]
    logger = Dependency[ILogger]

    def get_user(self, user_id: int) -> dict:
        """Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            The user data
        """
        self.logger.info(f"Getting user with ID: {user_id}")
        self.db.execute(f"SELECT * FROM users WHERE id = {user_id}")
        # In a real implementation, we would return actual data
        return {"id": user_id, "name": f"User {user_id}"}

    def save_user(self, user: dict) -> None:
        """Save a user.

        Args:
            user: The user data to save
        """
        self.logger.info(f"Saving user: {user}")
        self.db.execute(f"INSERT INTO users VALUES ({user})")


# Service that uses constructor injection
class UserService:
    """Example user service implementation."""

    def __init__(self, repository: IUserRepository, logger: ILogger):
        """Initialize the service with dependencies.

        Args:
            repository: The user repository
            logger: The logger
        """
        self.repository = repository
        self.logger = logger

    def process_user(self, user_id: int) -> dict:
        """Process a user.

        Args:
            user_id: The user ID

        Returns:
            The processed user data
        """
        self.logger.info(f"Processing user with ID: {user_id}")
        user = self.repository.get_user(user_id)
        # Do some processing
        user["processed"] = True
        self.repository.save_user(user)
        return user


# Configuration class
@dataclass
class AppConfig:
    """Application configuration."""

    db_connection_string: str
    log_level: str


# Example of a decorator that can be registered with the container
def logging_decorator(target: IUserRepository) -> IUserRepository:
    """Example decorator that adds logging to repository methods.

    Args:
        target: The repository to decorate

    Returns:
        The decorated repository
    """
    original_get_user = target.get_user
    original_save_user = target.save_user

    def get_user_with_logging(user_id: int) -> dict:
        print(f"DECORATOR: Before getting user {user_id}")
        result = original_get_user(user_id)
        print(f"DECORATOR: After getting user {user_id}")
        return result

    def save_user_with_logging(user: dict) -> None:
        print(f"DECORATOR: Before saving user {user}")
        original_save_user(user)
        print(f"DECORATOR: After saving user {user}")

    target.get_user = get_user_with_logging  # type: ignore
    target.save_user = save_user_with_logging  # type: ignore
    return target


# Example of a custom scope context for request-scoped dependencies
class RequestScopeContext(ScopeContext):
    """Example scope context for HTTP requests."""

    def __init__(self):
        """Initialize the request scope context."""
        self._active_scopes = {}
        self._current_scope = None

    def enter_scope(self, scope_id: str | None = None) -> str:
        """Enter a new request scope.

        Args:
            scope_id: Optional scope identifier

        Returns:
            The scope ID
        """
        actual_scope_id = scope_id or f"request_{id(self)}"
        self._active_scopes[actual_scope_id] = {}
        self._current_scope = actual_scope_id
        return actual_scope_id

    def exit_scope(self, scope_id: str) -> None:
        """Exit a request scope.

        Args:
            scope_id: The scope ID to exit
        """
        if scope_id in self._active_scopes:
            del self._active_scopes[scope_id]
            if self._current_scope == scope_id:
                self._current_scope = None

    def get_current_scope_id(self) -> str | None:
        """Get the current request scope ID.

        Returns:
            The current scope ID, or None if not in a scope
        """
        return self._current_scope

    @contextmanager
    def request(self):
        """Context manager for simulating an HTTP request.

        Yields:
            The request scope ID
        """
        scope_id = self.enter_scope()
        try:
            yield scope_id
        finally:
            self.exit_scope(scope_id)


def demonstrate_basic_usage():
    """Demonstrate basic container usage."""
    print("\n=== Basic Container Usage ===")

    # Create and configure a container
    container = Container()

    # Register services
    config = AppConfig(db_connection_string="example://localhost/db", log_level="INFO")
    container.register_instance(AppConfig, config)
    container.register_factory(IDatabase, lambda: Database(config.db_connection_string))
    container.register(ILogger, Logger)
    container.register(IUserRepository, UserRepository)
    container.register(UserService)

    # Resolve and use services
    user_service = container.resolve(UserService)
    processed_user = user_service.process_user(42)
    print(f"Processed user: {processed_user}")


def demonstrate_builder_pattern():
    """Demonstrate container builder pattern."""
    print("\n=== Container Builder Pattern ===")

    # Create a configuration
    config = AppConfig(db_connection_string="example://localhost/db", log_level="INFO")

    # Use the builder pattern
    builder = ContainerBuilder()
    builder.register_instance(AppConfig, config)
    builder.register_factory(IDatabase, lambda: Database(config.db_connection_string))
    builder.register(ILogger, Logger)
    builder.register(IUserRepository, UserRepository)
    builder.register(UserService)

    # Add a decorator
    builder.register_decorator(IUserRepository, logging_decorator)

    # Build the container
    container = builder.build()

    # Resolve and use services
    user_service = container.resolve(UserService)
    processed_user = user_service.process_user(123)
    print(f"Processed user: {processed_user}")


def demonstrate_scoped_dependencies():
    """Demonstrate scoped dependencies."""
    print("\n=== Scoped Dependencies ===")

    # Create a request scope context
    request_scope = RequestScopeContext()

    # Create a container with the request scope
    container = Container(scope_context=request_scope)

    # Register services
    config = AppConfig(db_connection_string="example://localhost/db", log_level="INFO")
    container.register_instance(AppConfig, config)
    container.register(ILogger, Logger, scope=Scope.SINGLETON)
    container.register_factory(
        IDatabase,
        lambda: Database(config.db_connection_string),
        scope=Scope.SCOPED,  # Database is scoped per request
    )
    container.register(IUserRepository, UserRepository, scope=Scope.SCOPED)
    container.register(UserService, scope=Scope.TRANSIENT)  # New instance each time

    # Simulate multiple requests
    with request_scope.request() as request1:
        print(f"\nRequest 1 (scope: {request1})")
        service1 = container.resolve(UserService)
        service1.process_user(1)

        # This will reuse the same database and repository instances
        service2 = container.resolve(UserService)
        service2.process_user(2)

    with request_scope.request() as request2:
        print(f"\nRequest 2 (scope: {request2})")
        # This will create new database and repository instances
        service3 = container.resolve(UserService)
        service3.process_user(3)


@inject
def function_with_injected_dependencies(repository: IUserRepository, logger: ILogger) -> None:
    """Function that uses dependency injection.

    Args:
        repository: The user repository (injected)
        logger: The logger (injected)
    """
    logger.info("Function called with injected dependencies")
    user = repository.get_user(999)
    repository.save_user(user)


def demonstrate_function_injection():
    """Demonstrate function parameter injection."""
    print("\n=== Function Parameter Injection ===")

    # Create and configure a container
    container = Container()

    # Register services
    config = AppConfig(db_connection_string="example://localhost/db", log_level="INFO")
    container.register_instance(AppConfig, config)
    container.register_factory(IDatabase, lambda: Database(config.db_connection_string))
    container.register(ILogger, Logger)
    container.register(IUserRepository, UserRepository)

    # Call the function without passing dependencies - they are injected
    function_with_injected_dependencies()


def demonstrate_declarative_dependencies():
    """Demonstrate declarative dependencies using descriptors."""
    print("\n=== Declarative Dependencies ===")

    # Create a container that holds only the low-level dependencies
    container = Container()
    config = AppConfig(db_connection_string="example://localhost/db", log_level="INFO")
    container.register_instance(AppConfig, config)
    container.register_factory(IDatabase, lambda: Database(config.db_connection_string))
    container.register(ILogger, Logger)

    # Create a repository that uses declarative dependencies
    repository = UserRepository()

    # The dependencies are automatically resolved when accessed
    repository.get_user(42)
    repository.save_user({"id": 42, "name": "Jane Doe"})


def main():
    """Run all demonstrations."""
    print("Enterprise-Grade DI Container Demonstrations")

    demonstrate_basic_usage()
    demonstrate_builder_pattern()
    demonstrate_scoped_dependencies()
    demonstrate_function_injection()
    demonstrate_declarative_dependencies()

    print("\nAll demonstrations complete!")


if __name__ == "__main__":
    main()
