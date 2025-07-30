"""Type definitions for the enterprise-grade dependency injection container.

This module contains all type definitions used by the DI container components,
keeping the type system centralized for better maintainability.
"""

from dataclasses import dataclass
from enum import Enum, auto
from functools import lru_cache
from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

# Type variables for generic type support
T = TypeVar("T")
TService = TypeVar("TService")
TImpl = TypeVar("TImpl", bound=Any)
TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TReturn = TypeVar("TReturn")
TParam = TypeVar("TParam")
# Covariant type for provider
T_co = TypeVar("T_co", covariant=True)

# Forward references
ContainerProtocol = Any  # Will be properly defined after Container class is created

# Factory related types
Factory = Callable[..., T]
FactoryWithDeps = Callable[[ContainerProtocol], T]


class Scope(Enum):
    """Scope of dependency registration.

    Attributes:
        SINGLETON: The dependency is created once and reused for all resolutions.
        TRANSIENT: The dependency is created anew for each resolution.
        SCOPED: The dependency is created once per scope (e.g., per thread, request, etc.).
    """

    SINGLETON = auto()
    TRANSIENT = auto()
    SCOPED = auto()


@runtime_checkable
class Provider(Protocol[T_co]):
    """Protocol for dependency providers.

    A provider is responsible for creating and managing instances of dependencies.
    Different providers implement different lifetime strategies.
    """

    def get(self) -> T_co:
        """Get an instance of the dependency.

        Returns:
            An instance of the dependency.
        """
        ...


@dataclass(frozen=True)
class RegistrationInfo:
    """Information about a registered dependency.

    This dataclass stores metadata about registered dependencies, including
    their type information, scope, and creation strategies.

    Attributes:
        service_type: The type that will be requested from the container.
        implementation_type: The concrete type that will be instantiated (if applicable).
        scope: The lifetime scope of the dependency.
        instance: A pre-created instance (for singleton registrations).
        factory: A factory function to create instances.
    """

    service_type: type[Any]
    implementation_type: type[Any] | None
    scope: Scope
    instance: Any | None = None
    factory: Factory[Any] | None = None


@runtime_checkable
class ScopeContext(Protocol):
    """Protocol for scope context management.

    A scope context manages the lifecycle of scoped dependencies.
    """

    def enter_scope(self, scope_id: str | None = None) -> str:
        """Enter a new scope context.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Returns:
            The scope ID.
        """
        ...

    def exit_scope(self, scope_id: str) -> None:
        """Exit a scope context, cleaning up any scoped dependencies.

        Args:
            scope_id: The scope ID to exit.
        """
        ...

    def get_current_scope_id(self) -> str | None:
        """Get the current scope ID.

        Returns:
            The current scope ID, or None if not in a scope.
        """
        ...


class DIException(Exception):
    """Base exception for dependency injection errors."""

    pass


class DependencyResolutionError(DIException):
    """Error raised when a dependency cannot be resolved.

    This could be due to missing registrations, type mismatches, or errors during instantiation.
    """

    pass


class DependencyRegistrationError(DIException):
    """Error raised when there's an error during dependency registration.

    This could be due to invalid service types, implementation types, or factory functions.
    """

    pass


class CircularDependencyError(DIException):
    """Error raised when a circular dependency is detected.

    Circular dependencies occur when a dependency depends on itself, either directly
    or through a chain of other dependencies.
    """

    pass


class ScopeError(DIException):
    """Error raised when there's an issue with scope management.

    This could be due to resolving scoped dependencies outside of a scope,
    or other scope-related issues.
    """

    pass


@dataclass(frozen=True)
class ResolveOptions:
    """Options for dependency resolution.

    Attributes:
        optional: If True, returns None instead of raising an error for unregistered dependencies.
        allow_auto_registration: If True, allows automatic registration of concrete types.
    """

    optional: bool = False
    allow_auto_registration: bool = True


@lru_cache(maxsize=128)
def get_constructor_params(cls: type[Any]) -> list[tuple[str, type[Any]]]:
    """Get constructor parameters with their types.

    This function uses introspection to analyze the constructor of a class
    and return its parameter information, cached for performance.

    Args:
        cls: The class to analyze.

    Returns:
        A list of (parameter_name, parameter_type) tuples.
    """
    import inspect

    try:
        sig = inspect.signature(cls.__init__)
        params = []

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.annotation == inspect.Parameter.empty:
                continue

            params.append((name, param.annotation))

        return params
    except (ValueError, TypeError):
        return []
