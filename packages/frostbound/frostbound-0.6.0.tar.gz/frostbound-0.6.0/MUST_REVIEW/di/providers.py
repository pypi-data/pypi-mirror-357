"""Provider implementations for the enterprise-grade dependency injection container.

This module contains various provider implementations for the container, which control
how dependencies are created, cached, and managed throughout their lifecycle.
"""

import inspect
import threading
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generic, Iterator, TypeVar, cast

from frostbound.di.types_ import (
    ContainerProtocol,
    Factory,
    Provider,
    ScopeContext,
    ScopeError,
    T_co,
    get_constructor_params,
)

try:
    from functools import cached_property
except ImportError:
    # For Python < 3.8
    from functools import lru_cache

    def cached_property(func):
        return property(lru_cache(maxsize=1)(func))


class InstanceProvider(Provider[T_co], Generic[T_co]):
    """Provider that returns a pre-created instance.

    This provider is the simplest one - it just returns a pre-created instance
    every time it's requested.
    """

    def __init__(self, instance: T_co) -> None:
        """Initialize with a specific instance.

        Args:
            instance: The instance to provide
        """
        self._instance = instance

    def get(self) -> T_co:
        """Get the pre-created instance.

        Returns:
            The instance
        """
        return self._instance


class FactoryProvider(Provider[T_co], Generic[T_co]):
    """Provider that creates instances using a factory function.

    This provider uses a factory function to create new instances
    on demand. It can also resolve the factory function's dependencies
    from the container.
    """

    def __init__(self, factory: Factory[T_co], container: ContainerProtocol) -> None:
        """Initialize with a factory function.

        Args:
            factory: The factory function
            container: The dependency container to resolve dependencies
        """
        self._factory = factory
        self._container = container

    def get(self) -> T_co:
        """Create an instance using the factory function.

        Returns:
            The created instance

        Raises:
            TypeError: If the factory is not callable
            ValueError: If a dependency cannot be resolved
        """
        # Create an OpenTelemetry span for tracing
        return self._resolve_factory()

    def _resolve_factory(self) -> T_co:
        """Resolve and call the factory with appropriate arguments.

        Returns:
            The created instance

        Raises:
            TypeError: If the factory is not callable
            ValueError: If a dependency cannot be resolved
        """
        if not callable(self._factory):
            raise TypeError(f"Factory must be callable, got {type(self._factory)}")

        # Get the factory's parameters
        params = inspect.signature(self._factory).parameters

        # Skip 'self' if it's the first parameter and we're dealing with a method
        params_list = list(params.values())
        if params_list and params_list[0].name == "self":
            params_list = params_list[1:]

        # For each parameter, try to resolve it from the container
        args = []
        kwargs = {}

        for param in params_list:
            # Skip kwargs with defaults
            if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default != inspect.Parameter.empty:
                continue

            if param.annotation != inspect.Parameter.empty:
                # Use the type annotation to resolve the dependency
                dependency_type = param.annotation
                try:
                    # For Optional types using | None syntax in Python 3.10+
                    if hasattr(dependency_type, "__origin__") and None.__class__ in getattr(
                        dependency_type, "__args__", ()
                    ):
                        try:
                            # Try to get the non-None type
                            actual_type = next(t for t in dependency_type.__args__ if t is not None.__class__)
                            dependency = self._container.resolve(actual_type)
                        except (StopIteration, AttributeError):
                            # If we can't extract the type or resolve it, use None
                            dependency = None
                    else:
                        # Regular type
                        dependency = self._container.resolve(dependency_type)

                    if param.kind == inspect.Parameter.KEYWORD_ONLY:
                        kwargs[param.name] = dependency
                    else:
                        args.append(dependency)
                except Exception as e:
                    # If the parameter has a default value, use it
                    if param.default != inspect.Parameter.empty:
                        if param.kind == inspect.Parameter.KEYWORD_ONLY:
                            kwargs[param.name] = param.default
                        continue

                    raise ValueError(
                        f"Failed to resolve dependency of type {dependency_type} for parameter {param.name}: {str(e)}"
                    ) from e
            elif param.default != inspect.Parameter.empty:
                # Skip parameters with default values
                continue
            else:
                # Can't determine the dependency
                raise ValueError(
                    f"Cannot resolve dependency for parameter {param.name} without type annotation or default value"
                )

        # Call the factory with the resolved dependencies
        if kwargs:
            return self._factory(*args, **kwargs)
        return self._factory(*args)


class SingletonProvider(Provider[T_co], Generic[T_co]):
    """Provider that creates instances once and caches them.

    This provider ensures that only one instance of a dependency exists
    throughout the application's lifetime.
    """

    def __init__(self, factory_provider: FactoryProvider[T_co]) -> None:
        """Initialize with a factory provider.

        Args:
            factory_provider: The provider that creates the instance
        """
        self._factory_provider = factory_provider
        self._instance: T_co | None = None
        self._lock = threading.RLock()

    def get(self) -> T_co:
        """Get or create the singleton instance.

        Returns:
            The singleton instance
        """
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory_provider.get()
        return cast(T_co, self._instance)


class TransientProvider(Provider[T_co], Generic[T_co]):
    """Provider that creates a new instance on every get call.

    This provider always creates a fresh instance, which is useful for
    stateful dependencies that should not be shared.
    """

    def __init__(self, factory_provider: FactoryProvider[T_co]) -> None:
        """Initialize with a factory provider.

        Args:
            factory_provider: The provider that creates the instance
        """
        self._factory_provider = factory_provider

    def get(self) -> T_co:
        """Create a new instance.

        Returns:
            The new instance
        """
        return self._factory_provider.get()


class ScopedProvider(Provider[T_co], Generic[T_co]):
    """Provider that creates instances scoped to a lifecycle.

    This provider creates one instance per scope (e.g., per request, thread, etc.).
    It requires a scope context to manage instance lifecycles.
    """

    def __init__(self, factory_provider: FactoryProvider[T_co], scope_context: ScopeContext | None = None) -> None:
        """Initialize with a factory provider and optional scope context.

        Args:
            factory_provider: The provider that creates the instance
            scope_context: The context that manages scopes. If None, uses ThreadScopeContext.
        """
        self._factory_provider = factory_provider
        self._scope_context = scope_context or ThreadScopeContext()
        self._instances: Dict[str, T_co] = {}
        self._lock = threading.RLock()

    def get(self) -> T_co:
        """Get or create the scoped instance.

        Returns:
            The scoped instance

        Raises:
            ScopeError: If no active scope is found
        """
        # Get the current scope ID
        scope_id = self._scope_context.get_current_scope_id()
        if scope_id is None:
            raise ScopeError("Cannot resolve scoped dependency outside of a scope")

        if scope_id not in self._instances:
            with self._lock:
                if scope_id not in self._instances:
                    self._instances[scope_id] = self._factory_provider.get()

        return self._instances[scope_id]

    def clear_scope(self, scope_id: str | None = None) -> None:
        """Clear the instance for a specific scope or the current scope.

        Args:
            scope_id: The scope ID to clear, or None for the current scope

        Raises:
            ScopeError: If no active scope is found and scope_id is None
        """
        with self._lock:
            if scope_id is None:
                scope_id = self._scope_context.get_current_scope_id()
                if scope_id is None:
                    raise ScopeError("Cannot clear scope when no scope is active")

            if scope_id in self._instances:
                del self._instances[scope_id]

    def clear_all_scopes(self) -> None:
        """Clear all scoped instances."""
        with self._lock:
            self._instances.clear()


class ThreadScopeContext(ScopeContext):
    """A scope context that uses thread ID as the scope identifier.

    This is a simple implementation that treats each thread as a separate scope.
    """

    def __init__(self) -> None:
        """Initialize the thread scope context."""
        self._active_scopes: Dict[str, int] = {}
        self._lock = threading.RLock()

    def enter_scope(self, scope_id: str | None = None) -> str:
        """Enter a new scope context.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Returns:
            The scope ID.
        """
        with self._lock:
            thread_id = threading.get_ident()
            actual_scope_id = scope_id or f"thread_{thread_id}_{uuid.uuid4().hex[:8]}"
            self._active_scopes[actual_scope_id] = thread_id
            return actual_scope_id

    def exit_scope(self, scope_id: str) -> None:
        """Exit a scope context.

        Args:
            scope_id: The scope ID to exit.
        """
        with self._lock:
            if scope_id in self._active_scopes:
                del self._active_scopes[scope_id]

    def get_current_scope_id(self) -> str | None:
        """Get the current scope ID.

        Returns:
            The current scope ID, or None if not in a scope.
        """
        thread_id = threading.get_ident()
        # Find a scope for this thread
        for scope_id, tid in self._active_scopes.items():
            if tid == thread_id:
                return scope_id
        return None

    @contextmanager
    def scope(self, scope_id: str | None = None) -> Iterator[str]:
        """Context manager for scope handling.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Yields:
            The scope ID.
        """
        sid = self.enter_scope(scope_id)
        try:
            yield sid
        finally:
            self.exit_scope(sid)


class AsyncScopeContext(ScopeContext):
    """A scope context for asynchronous operations.

    This implementation uses an asyncio-compatible approach to maintain
    scopes across asynchronous operations.
    """

    def __init__(self) -> None:
        """Initialize the async scope context."""
        self._active_scopes: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._context_var = None

        # Try to import contextvars (Python 3.7+)
        try:
            import contextvars

            self._context_var = contextvars.ContextVar("scope_id", default=None)
        except ImportError:
            self._context_var = None

    def enter_scope(self, scope_id: str | None = None) -> str:
        """Enter a new scope context.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Returns:
            The scope ID.
        """
        with self._lock:
            actual_scope_id = scope_id or f"async_{uuid.uuid4().hex}"
            self._active_scopes[actual_scope_id] = True

            if self._context_var is not None:
                self._context_var.set(actual_scope_id)

            return actual_scope_id

    def exit_scope(self, scope_id: str) -> None:
        """Exit a scope context.

        Args:
            scope_id: The scope ID to exit.
        """
        with self._lock:
            if scope_id in self._active_scopes:
                del self._active_scopes[scope_id]

            if self._context_var is not None and self._context_var.get() == scope_id:
                self._context_var.set(None)

    def get_current_scope_id(self) -> str | None:
        """Get the current scope ID.

        Returns:
            The current scope ID, or None if not in a scope.
        """
        if self._context_var is not None:
            return self._context_var.get()
        return None

    @contextmanager
    def scope(self, scope_id: str | None = None) -> Iterator[str]:
        """Context manager for scope handling.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Yields:
            The scope ID.
        """
        sid = self.enter_scope(scope_id)
        try:
            yield sid
        finally:
            self.exit_scope(sid)


class LazyProvider(Provider[T_co], Generic[T_co]):
    """Provider that creates instances on first use and caches them.

    Similar to SingletonProvider but with lazy initialization semantics.
    """

    def __init__(self, factory_provider: FactoryProvider[T_co]) -> None:
        """Initialize with a factory provider.

        Args:
            factory_provider: The provider that creates the instance
        """
        self._factory_provider = factory_provider
        self._lock = threading.RLock()

    @cached_property
    def _instance(self) -> T_co:
        """Lazily create and cache the instance.

        Returns:
            The cached instance
        """
        with self._lock:
            return self._factory_provider.get()

    def get(self) -> T_co:
        """Get the lazily created instance.

        Returns:
            The instance
        """
        return self._instance
