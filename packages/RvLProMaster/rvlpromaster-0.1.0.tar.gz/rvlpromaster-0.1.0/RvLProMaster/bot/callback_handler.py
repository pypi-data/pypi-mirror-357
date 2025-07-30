from typing import Callable, Dict, Awaitable, Any
from functools import wraps

pick_callback_button: Dict[str, Callable[[], Awaitable[Any]]] = {}

def HandleButton(callback_data: str) -> Callable[[Callable[[], Awaitable[Any]]], Callable[[], Awaitable[Any]]]:
    """Use this decorator to Handle Button.

    Args:
        callback_data (str): Your Button Callback data. example: "btn1"
    """
    def decorator(func: Callable[[], Awaitable[Any]]) -> Callable[[], Awaitable[Any]]:
        @wraps(func)
        async def wrapper() -> Any:
            return await func()
        pick_callback_button[callback_data] = wrapper
        return wrapper
    return decorator