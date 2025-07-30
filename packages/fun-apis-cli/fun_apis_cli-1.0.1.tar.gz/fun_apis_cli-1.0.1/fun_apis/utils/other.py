import os
from typing import Callable, Any 
from functools import wraps
from time import perf_counter
from fun_apis.constants import console

# For testing purposes
def measure_function_execution_time(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        console.print(f"\"{func.__name__}\" Function done within {end - start: .2f} s.")
        return result
    return wrapper

def clear_screen() -> None:
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')