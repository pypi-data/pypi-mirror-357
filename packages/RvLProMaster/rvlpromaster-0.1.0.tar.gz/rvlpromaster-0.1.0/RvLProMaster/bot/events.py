from typing import Callable, Dict, Awaitable, Any, Literal
from functools import wraps

event_pick: Dict[str, Callable[[], Awaitable[Any]]] = {}


def EventWatcher(event_list: Literal["UserRequest", "UserJoined", "UserLeft"]) -> Callable[[Callable[[], Awaitable[Any]]], Callable[[], Awaitable[Any]]]:
    """Use this decorator to EventWatcher in the bot.

    Args:
        event_list (str): Your event name. Example: UserRequest.
    """
    def decorator(func: Callable[[], Awaitable[Any]]) -> Callable[[], Awaitable[Any]]:
        @wraps(func)
        async def wrapper() -> Any:
            return await func()
        event_pick[event_list] = wrapper
        return wrapper
    return decorator


