"""
Examples of using the retry mechanism.

This module demonstrates how to use the retry mechanism in different ways.
"""

import logging
import random
import time
from typing import Any, Dict

from frostbound.resilience.retry import Retry, retry

# Configure logging to show debug messages
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Specifically enable debug logs for the retry logger


# Example 1: Basic usage as a decorator
@retry(max_attempts=3)
def flaky_network_call() -> str:
    """Simulate a flaky network call that occasionally fails."""
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("Network connection failed")
    return "Success!"


# Example 2: More complex decorator configuration
@Retry(
    max_attempts=10,
    base_delay=0.2,
    max_delay=2.0,
    jitter=0.2,
    retry_on_exceptions=[ValueError, TimeoutError],
)
def process_data(data: dict[str, Any]) -> dict[str, Any]:
    """Process data with retries on specific exceptions."""
    if random.random() < 0.5:  # 40% chance of ValueError
        raise ValueError("Invalid data format")
    if random.random() < 0.5:  # 30% chance of TimeoutError
        raise TimeoutError("Processing timed out")

    # Process the data
    result = {"processed": True, "source": data}

    return result


# Example 3: Retry based on result
@Retry(
    max_attempts=4,
    retry_on_result=lambda result: result.get("status") == "PENDING",
)
def check_job_status(job_id: str) -> Dict[str, str]:
    """Check job status, retrying if it's still pending."""
    # Simulate a job that takes time to complete
    statuses = ["PENDING", "PENDING", "PENDING", "COMPLETED"]
    status = statuses[min(len(statuses) - 1, random.randint(0, 3))]
    return {"job_id": job_id, "status": status}


# Example 4: Using as a context manager
def upload_file_with_retry(file_path: str) -> bool:
    """Upload a file with retries using the context manager pattern."""
    # Create a retry instance with custom settings
    upload_retry = Retry(
        max_attempts=3,
        base_delay=0.5,
        stop_after_delay=10.0,  # Give up after 10 seconds total
    )

    # Use the retry instance as a context manager
    with upload_retry.calling(simulate_file_upload) as retry_ctx:
        # Call the function with the retry context
        return retry_ctx(file_path)


def simulate_file_upload(file_path: str) -> bool:
    """Simulate a file upload that might fail."""
    if random.random() < 0.6:  # 60% chance of failure
        raise ConnectionError(f"Failed to upload {file_path}")
    return True


# Example 5: Combining with asyncio (conceptual - would need asyncio support)
# This shows how you might want to extend the retry mechanism in the future
def process_batch_with_retry(items: list[str]) -> dict[str, Any]:
    """Process a batch of items with retry, demonstrating more complex usage."""
    results = {"succeeded": [], "failed": []}

    # Create a custom retry configuration
    batch_retry = Retry(
        max_attempts=3,
        base_delay=0.1,
        jitter=0.1,
        retry_on_exceptions=[ConnectionError, TimeoutError],
    )

    for item in items:
        try:
            # Use the retry to process each item
            with batch_retry.calling(process_item) as retry_ctx:
                result = retry_ctx(item)
                results["succeeded"].append({"item": item, "result": result})
        except Exception as e:
            # Track failed items after retries are exhausted
            results["failed"].append({"item": item, "error": str(e)})

    return results


def process_item(item: str) -> str:
    """Process a single item with potential for failure."""
    # Simulate processing
    if random.random() < 0.4:  # 40% chance of failure
        if random.random() < 0.5:
            raise ConnectionError(f"Connection error processing {item}")
        else:
            raise TimeoutError(f"Timeout processing {item}")

    time.sleep(0.1)  # Simulate processing time
    return f"Processed {item}"


if __name__ == "__main__":
    # Run the examples
    print("\n=== Example 1: Basic decorator usage ===")
    try:
        result = flaky_network_call()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")

    print("\n=== Example 2: Decorator with custom configuration ===")
    try:
        result = process_data({"key": "value"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")

    print("\n=== Example 3: Retry based on result ===")
    try:
        result = check_job_status("job-123")
        print(f"Final job status: {result}")
    except Exception as e:
        print(f"Failed to check job status: {e}")

    print("\n=== Example 4: Context manager usage ===")
    try:
        result = upload_file_with_retry("example.txt")
        print(f"Upload successful: {result}")
    except Exception as e:
        print(f"Upload failed after retries: {e}")

    print("\n=== Example 5: Batch processing with retry ===")
    items = ["item1", "item2", "item3", "item4", "item5"]
    results = process_batch_with_retry(items)
    print(f"Succeeded: {len(results['succeeded'])} items")
    print(f"Failed: {len(results['failed'])} items")
