from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

def ensure_coroutine(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to ensure a function returns a coroutine.

    If the function is not async, it wraps the result in a coroutine.
    """
def run_async_in_sync(coro: Any) -> Any:
    """
    Run an async coroutine in a sync context.

    Handles both cases where an event loop is already running and when it's not.
    """
def safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    """
    Safely get an attribute from an object.

    Returns the default value if the attribute doesn't exist or if accessing it raises an exception.
    """
def safe_isinstance(obj: Any, class_or_tuple: type | tuple[type, ...]) -> bool:
    """
    Safely check if an object is an instance of a type.

    Returns False if isinstance raises an exception.
    """
def safe_issubclass(cls, class_or_tuple: type | tuple[type, ...]) -> bool:
    """
    Safely check if a class is a subclass of another class.

    Returns False if issubclass raises an exception.
    """
def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
def filter_none_values(d: dict[str, Any]) -> dict[str, Any]:
    """
    Filter out None values from a dictionary.

    Args:
        d: Dictionary to filter

    Returns:
        Dictionary with None values removed
    """
def get_class_name(cls) -> str:
    """
    Get the name of a class, handling various edge cases.

    Args:
        cls: Class or object to get name from

    Returns:
        Class name as string
    """
def get_module_name(cls) -> str:
    """
    Get the module name of a class.

    Args:
        cls: Class or object to get module name from

    Returns:
        Module name as string
    """
def create_unique_key(*parts: Any) -> str:
    """
    Create a unique key from multiple parts.

    Args:
        *parts: Parts to combine into a key

    Returns:
        Unique key string
    """
def truncate_string(s: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
