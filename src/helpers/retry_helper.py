"""Module to retry an operation up to max_retries times, waiting delay seconds between attempts."""

import time


def retry_operation(*args, operation, max_retries=5, delay=10, **kwargs):
    """Retry an operation up to max_retries times, waiting delay seconds between attempts."""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt+1} failed: {e}. Retrying in {delay} seconds..."
                )
                time.sleep(delay)
            else:
                print(f"All {max_retries} attempts failed.")
    if last_exception is not None:
        raise last_exception
    raise Exception("Operation failed after retries, but no exception was captured.")
