import asyncio
import time

from frostbound.instrumentation.timer import timer

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Test as sync decorator
@timer
def test_sync() -> str:
    """Sync function for testing."""
    time.sleep(0.5)
    return "sync result"


# Test as async decorator
@timer
async def test_async() -> str:
    """Async function for testing."""
    await asyncio.sleep(0.5)
    return "async result"


# Test as sync context manager
def test_sync_ctx() -> str:
    """Sync context manager test."""
    with Timer[str](name="test_sync_ctx") as t:
        time.sleep(0.5)
        logger.info(f"Inside sync context. Current time: {t.execution_time:.4f}")
    logger.info(f"Finished sync context. Final time: {t.execution_time:.4f}")
    return "sync ctx result"


# Test as async context manager
async def test_async_ctx() -> str:
    """Async context manager test."""
    async with Timer[str](name="test_async_ctx") as t:
        await asyncio.sleep(0.5)
        logger.info(f"Inside async context. Current time: {t.execution_time:.4f}")
    logger.info(f"Finished async context. Final time: {t.execution_time:.4f}")
    return "async ctx result"


# Test error handling in sync decorator
@timer
def test_sync_error() -> None:
    """Sync function that raises an error."""
    time.sleep(0.5)
    raise ValueError("Test error in sync function")


# Test error handling in async decorator
@timer
async def test_async_error() -> None:
    """Async function that raises an error."""
    await asyncio.sleep(0.5)
    raise ValueError("Test error in async function")


# Test error handling in sync context manager
def test_sync_ctx_error() -> str:
    """Sync context manager error test."""
    try:
        with Timer(name="test_sync_ctx_error"):
            time.sleep(0.5)
            raise ValueError("Test error in sync context")
    except ValueError:
        logger.info("Successfully caught error in sync context")
        return "Error caught in sync context"


# Test error handling in async context manager
async def test_async_ctx_error() -> str:
    """Async context manager error test."""
    try:
        async with Timer(name="test_async_ctx_error"):
            await asyncio.sleep(0.5)
            raise ValueError("Test error in async context")
    except ValueError:
        logger.info("Successfully caught error in async context")
        return "Error caught in async context"


# Test nested timers (decorator inside context manager)
def test_nested_sync() -> str:
    """Nested sync timers test."""
    with Timer(name="outer_sync"):
        time.sleep(0.2)  # Outer timer
        result, _ = test_sync()  # Inner timer (decorator), ignore time tuple
        time.sleep(0.2)  # Outer timer
        return result  # Return original result


# Test nested timers (context manager inside decorator)
@timer
def test_nested_sync_reversed() -> str:
    """Nested sync timers reversed test."""
    time.sleep(0.2)  # Part of outer decorated function
    with Timer(name="inner_sync_reversed"):
        time.sleep(0.5)  # Inner timer
    time.sleep(0.2)  # Part of outer decorated function
    return "nested reversed result"


# Test nested async timers (decorator inside context manager)
async def test_nested_async() -> str:
    """Nested async timers test."""
    async with Timer[str](name="outer_async"):
        await asyncio.sleep(0.2)  # Outer timer
        # We need to properly call the async function
        timer_coro = test_async()  # This returns a coroutine
        result_and_time = await timer_coro
        result: str
        result, _ = result_and_time  # Unpack the tuple
        await asyncio.sleep(0.2)  # Outer timer
        return result  # Return original result


# Test nested async timers reversed (context manager inside decorator)
@timer
async def test_nested_async_reversed() -> str:
    """Nested async timers reversed test."""
    await asyncio.sleep(0.2)  # Part of outer decorated function
    async with Timer(name="inner_async_reversed"):
        await asyncio.sleep(0.5)  # Inner timer
    await asyncio.sleep(0.2)  # Part of outer decorated function
    return "nested async reversed result"


# Run the tests
async def main() -> None:  # Added return type hint
    """Main function to run all tests."""
    print("==== Testing basic functionality ====")

    # Test sync decorator
    result1, time1 = test_sync()
    print(f"Sync decorator result: {result1} (took {time1:.4f}s)")

    # Test sync context manager
    result2 = test_sync_ctx()
    print(f"Sync context manager result: {result2}")

    # Test async decorator
    # Properly handle the async function call
    timer_coro3 = test_async()  # This returns a coroutine
    result_and_time3 = await timer_coro3
    result3, time3 = result_and_time3  # Unpack the tuple
    print(f"Async decorator result: {result3} (took {time3:.4f}s)")

    # Test async context manager
    result4 = await test_async_ctx()
    print(f"Async context manager result: {result4}")

    print("\n==== Testing error handling ====")

    # Test sync decorator error
    try:
        test_sync_error()
    except ValueError as e:
        logger.info(f"Caught expected error in sync decorator: {e}")

    # Test async decorator error
    try:
        # Properly handle the async function call
        timer_coro_err = test_async_error()  # This returns a coroutine
        result_and_time_err = await timer_coro_err
        result_err, _ = result_and_time_err  # Unpack tuple
    except ValueError as e:
        logger.info(f"Caught expected error in async decorator: {e}")

    print("\n==== Testing nested timers ====")

    # Test nested sync timers
    result7 = test_nested_sync()
    print(f"Nested sync timers result: {result7}")

    # Test nested sync timers reversed
    result8, time8 = test_nested_sync_reversed()
    print(f"Nested sync timers reversed result: {result8} (took {time8:.4f}s)")

    # Test nested async timers
    result9 = await test_nested_async()
    print(f"Nested async timers result: {result9}")

    # Test nested async timers reversed
    # Properly handle the async function call
    timer_coro10 = test_nested_async_reversed()  # This returns a coroutine
    result_and_time10 = await timer_coro10
    result10, time10 = result_and_time10  # Unpack tuple
    print(f"Nested async timers reversed result: {result10} (took {time10:.4f}s)")


if __name__ == "__main__":
    asyncio.run(main())
