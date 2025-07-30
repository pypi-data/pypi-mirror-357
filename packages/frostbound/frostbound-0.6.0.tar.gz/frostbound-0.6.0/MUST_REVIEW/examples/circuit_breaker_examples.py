"""
Examples of using the circuit breaker pattern.

This module demonstrates how to use the circuit breaker in different ways.
"""

import random
import time
from typing import Any, Dict

from instrumentation.resilience.circuit_breaker import (CircuitBreaker,
                                                        CircuitBreakerError,
                                                        circuit_breaker)


# Example 1: Basic usage as a decorator
@circuit_breaker(failure_threshold=3, reset_timeout_seconds=5.0)
def call_external_api() -> Dict[str, Any]:
    """Simulate an API call that might fail."""
    # Simulate random failures
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("External API connection failed")

    return {"status": "success", "data": "API response"}


# Example 2: Using a fallback
def fallback_response(*args, **kwargs) -> Dict[str, Any]:
    """Fallback function when the circuit is open."""
    return {"status": "fallback", "data": "Cached response"}


@circuit_breaker(
    failure_threshold=2,
    reset_timeout_seconds=5.0,
    fallback=fallback_response,
)
def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get user data from an external service with fallback."""
    if random.random() < 0.6:  # 60% chance of failure
        raise TimeoutError(f"Timeout fetching data for user {user_id}")

    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "status": "active",
    }


# Example 3: Manual usage with CircuitBreakerState
def process_payment(payment_id: str, amount: float, circuit_state) -> Dict[str, Any]:
    """Process a payment with manual circuit breaker handling."""
    # Check if circuit allows execution
    if not circuit_state.should_execute():
        raise CircuitBreakerError("Payment service circuit is open")

    try:
        # Simulate payment processing
        if random.random() < 0.5:  # 50% chance of failure
            raise ConnectionError("Payment gateway connection failed")

        # Payment successful
        circuit_state.record_success()
        return {
            "payment_id": payment_id,
            "amount": amount,
            "status": "processed",
            "timestamp": time.time(),
        }
    except Exception as e:
        # Record failure
        circuit_state.record_failure()
        raise


# Example 4: Using as a context manager
def fetch_data_with_circuit_breaker() -> Dict[str, Any]:
    """Fetch data using circuit breaker as a context manager."""
    # Create a circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=3,
        reset_timeout_seconds=5.0,
    )

    try:
        # Use circuit breaker as a context manager
        with breaker.context() as state:
            # Simulate API call
            if random.random() < 0.6:  # 60% chance of failure
                raise ConnectionError("API connection failed")

            return {"status": "success", "data": "API response"}
    except CircuitBreakerError as e:
        # Circuit is open
        return {"status": "error", "message": str(e)}
    except Exception as e:
        # Other error (circuit failure will be recorded automatically)
        return {"status": "error", "message": str(e)}


# Example 5: More complex usage with multiple services
class ServiceRegistry:
    """Registry of services with circuit breakers."""

    def __init__(self) -> None:
        """Initialize service registry."""
        self.circuit_breakers = {
            "auth": CircuitBreaker(failure_threshold=5, reset_timeout_seconds=10.0),
            "payment": CircuitBreaker(failure_threshold=2, reset_timeout_seconds=30.0),
            "inventory": CircuitBreaker(
                failure_threshold=3, reset_timeout_seconds=15.0
            ),
        }

    def call_service(
        self, service_name: str, operation: str, **params
    ) -> Dict[str, Any]:
        """Call a service with circuit breaker protection."""
        if service_name not in self.circuit_breakers:
            raise ValueError(f"Unknown service: {service_name}")

        breaker = self.circuit_breakers[service_name]

        try:
            # Execute service call with circuit breaker
            return breaker.execute(
                self._simulate_service_call,
                service_name=service_name,
                operation=operation,
                **params,
            )
        except CircuitBreakerError as e:
            # Circuit is open
            return {
                "status": "error",
                "service": service_name,
                "message": f"Service unavailable: {str(e)}",
            }
        except Exception as e:
            # Other error
            return {
                "status": "error",
                "service": service_name,
                "message": str(e),
            }

    def _simulate_service_call(
        self,
        service_name: str,
        operation: str,
        **params,
    ) -> Dict[str, Any]:
        """Simulate a service call that might fail."""
        # Different failure rates for different services
        failure_rates = {
            "auth": 0.3,
            "payment": 0.5,
            "inventory": 0.4,
        }

        failure_rate = failure_rates.get(service_name, 0.5)

        if random.random() < failure_rate:
            raise ConnectionError(f"{service_name} service connection failed")

        # Successful response
        return {
            "status": "success",
            "service": service_name,
            "operation": operation,
            "params": params,
            "result": f"{operation} completed successfully",
        }


def run_examples() -> None:
    """Run all circuit breaker examples."""
    # Example 1: Basic decorator usage
    print("\n=== Example 1: Basic Decorator Usage ===")
    for i in range(5):
        try:
            result = call_external_api()
            print(f"Call {i+1}: Success - {result}")
        except Exception as e:
            print(f"Call {i+1}: Error - {type(e).__name__}: {str(e)}")

    # Example 2: Using a fallback
    print("\n=== Example 2: Using a Fallback ===")
    for i in range(5):
        try:
            result = get_user_data(f"user{i}")
            print(f"Call {i+1}: {result}")
        except Exception as e:
            print(f"Call {i+1}: Error - {type(e).__name__}: {str(e)}")

    # Example 3: Manual usage
    print("\n=== Example 3: Manual Circuit Breaker Usage ===")
    from instrumentation.resilience.circuit_breaker import CircuitBreakerState

    payment_circuit = CircuitBreakerState(
        failure_threshold=2, reset_timeout_seconds=5.0
    )

    for i in range(5):
        try:
            result = process_payment(f"payment{i}", 100.0 * (i + 1), payment_circuit)
            print(f"Payment {i+1}: Success - {result}")
        except Exception as e:
            print(f"Payment {i+1}: Error - {type(e).__name__}: {str(e)}")

    # Example 4: Context manager
    print("\n=== Example 4: Context Manager Usage ===")
    for i in range(5):
        result = fetch_data_with_circuit_breaker()
        print(f"Call {i+1}: {result}")

    # Example 5: Service registry
    print("\n=== Example 5: Service Registry ===")
    registry = ServiceRegistry()

    services = ["auth", "payment", "inventory"]
    operations = ["validate", "process", "check"]

    for i in range(10):
        service = random.choice(services)
        operation = random.choice(operations)

        result = registry.call_service(
            service_name=service,
            operation=operation,
            user_id=f"user{i}",
            transaction_id=f"txn{i}",
        )

        print(f"Call {i+1}: {service}.{operation} - {result['status']}")


if __name__ == "__main__":
    run_examples()
