from typing import Callable, Dict, Awaitable, Any
from functools import wraps

pick_command: Dict[str, Callable[[], Awaitable[Any]]] = {}

def BotCommands(command: str) -> Callable[[Callable[[], Awaitable[Any]]], Callable[[], Awaitable[Any]]]:
    """Use this decorator to register a command in the bot.

    Args:
        command (str): Your command name. Example: /start, /help, etc.
    """
    def decorator(func: Callable[[], Awaitable[Any]]) -> Callable[[], Awaitable[Any]]:
        @wraps(func)
        async def wrapper() -> Any:
            return await func()
        pick_command[command] = wrapper
        return wrapper
    return decorator
