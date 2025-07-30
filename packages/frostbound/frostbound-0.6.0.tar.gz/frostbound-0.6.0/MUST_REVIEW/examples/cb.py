import asyncio
import logging
import random
import time
from typing import Any, Dict

from frostbound.resilience.circuit_breaker import circuit_breaker

# Set up logging to see circuit breaker state changes
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ---------------------------------------------------------
# Synchronous example with simulated failures
# ---------------------------------------------------------

# Counter to track calls and force failures
call_count = 0

def default_user(user_id: int) -> Dict[str, Any]:
    """Fallback function that returns default user data."""
    return {"id": user_id, "name": "Default User", "status": "fallback"}

@circuit_breaker(failure_threshold=3, reset_timeout_seconds=5, fallback=default_user)
def get_user_data(user_id: int) -> Dict[str, Any]:
    """
    Simulate an API call that fails after a certain number of attempts.
    This lets us test the circuit breaker without external dependencies.
    """
    global call_count
    call_count += 1

    print(f"Attempting to get user data (call #{call_count})...")

    # Simulate failures for the first 5 calls
    if call_count <= 5:
        print("Service unavailable!")
        raise ConnectionError("Service temporarily unavailable")

    # After that, return success to test circuit recovery
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "status": "active"
    }

def run_sync_example():
    """Run the synchronous circuit breaker example."""
    print("\n===== SYNCHRONOUS CIRCUIT BREAKER EXAMPLE =====\n")

    # Make several calls - first few will fail normally
    for i in range(1, 5):
        try:
            result = get_user_data(123)
            print(f"Call {i} - Success: {result}\n")
        except Exception as e:
            print(f"Call {i} - Error: {e}\n")
        time.sleep(0.5)

    # After failure threshold (3), circuit should be OPEN
    # The next calls should immediately return the fallback without trying
    print("Circuit should now be OPEN. Using fallback...")
    for i in range(5, 7):
        try:
            result = get_user_data(123)
            print(f"Call {i} - Got fallback: {result}\n")
        except Exception as e:
            print(f"Call {i} - Error: {e}\n")
        time.sleep(0.5)

    # Wait for reset timeout to let circuit go to HALF-OPEN
    print(f"Waiting for reset timeout (5 seconds)...")
    time.sleep(5.5)

    # Now one request should be allowed through as a test
    # Since we've set our function to succeed after 5 failures,
    # this should succeed and reset the circuit to CLOSED
    print("Circuit should now be HALF-OPEN. Testing with one request...")
    try:
        result = get_user_data(123)
        print(f"Test request succeeded: {result}\n")
    except Exception as e:
        print(f"Test request failed: {e}\n")

    # Final request with closed circuit should work
    print("Circuit should now be CLOSED again. Making final request...")
    try:
        result = get_user_data(123)
        print(f"Final request: {result}\n")
    except Exception as e:
        print(f"Final request error: {e}\n")

# ---------------------------------------------------------
# Asynchronous example
# ---------------------------------------------------------

async_call_count = 0

async def async_fallback(user_id: int) -> Dict[str, Any]:
    """Async fallback function."""
    await asyncio.sleep(0.1)  # Simulate some async operation
    return {"id": user_id, "name": "Default User", "status": "async-fallback"}

@circuit_breaker(failure_threshold=3, reset_timeout_seconds=5, fallback=async_fallback)
async def fetch_user_async(user_id: int) -> Dict[str, Any]:
    """Simulated async API call with controlled failures."""
    global async_call_count
    async_call_count += 1

    print(f"Async call #{async_call_count} - Attempting to fetch user {user_id}...")

    # Simulate network delay
    await asyncio.sleep(0.2)

    # Simulate failures for the first 5 calls
    if async_call_count <= 5:
        print("Async service unavailable!")
        raise ConnectionError("Async service temporarily unavailable")

    # After that, success
    return {
        "id": user_id,
        "name": f"Async User {user_id}",
        "email": f"async{user_id}@example.com",
        "status": "active"
    }

async def run_async_example():
    """Run the asynchronous circuit breaker example."""
    print("\n===== ASYNCHRONOUS CIRCUIT BREAKER EXAMPLE =====\n")

    # Make several calls - first few will fail normally
    for i in range(1, 5):
        try:
            result = await fetch_user_async(456)
            print(f"Async call {i} - Success: {result}\n")
        except Exception as e:
            print(f"Async call {i} - Error: {e}\n")
        await asyncio.sleep(0.5)

    # After failure threshold, circuit should be OPEN
    print("Circuit should now be OPEN. Using fallback...")
    for i in range(5, 7):
        try:
            result = await fetch_user_async(456)
            print(f"Async call {i} - Got fallback: {result}\n")
        except Exception as e:
            print(f"Async call {i} - Error: {e}\n")
        await asyncio.sleep(0.5)

    # Wait for reset timeout
    print(f"Waiting for reset timeout (5 seconds)...")
    await asyncio.sleep(5.5)

    # Now one request should be allowed through to test
    print("Circuit should now be HALF-OPEN. Testing with one request...")
    try:
        result = await fetch_user_async(456)
        print(f"Async test request succeeded: {result}\n")
    except Exception as e:
        print(f"Async test request failed: {e}\n")

    # Final request with closed circuit
    print("Circuit should now be CLOSED again. Making final request...")
    try:
        result = await fetch_user_async(456)
        print(f"Async final request: {result}\n")
    except Exception as e:
        print(f"Async final request error: {e}\n")

async def main():
    # Run synchronous example first
    run_sync_example()

    # Then run async example
    await run_async_example()

if __name__ == "__main__":
    asyncio.run(main())