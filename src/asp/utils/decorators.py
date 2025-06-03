import time
import logfire
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    A decorator that retries a function call a specified number of times with a delay.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts:
                        logfire.warn("Attempt {attempt} failed for {func_name}. Retrying in {delay:.2f} seconds.",
                                     attempt=attempt, func_name=func.__name__, delay=delay)
                        time.sleep(delay)
                    else:
                        logfire.error("Attempt {attempt} failed for {func_name}. No more retries.",
                                      attempt=attempt, func_name=func.__name__, error=e, exc_info=True)
                        raise
        return wrapper
    return decorator