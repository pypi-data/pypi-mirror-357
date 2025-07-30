"""Tracks utils."""

import functools
import logging
import threading
from collections.abc import Callable
from typing import ParamSpec, TypeVar

LOGGER = logging.getLogger(__name__)
P = ParamSpec("P")
T = TypeVar("T")


def fire_and_forget(func: Callable[P, T]) -> Callable[P, None]:
    """Make a function fire-and-forget."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        def run() -> None:
            try:
                func(*args, **kwargs)
            except Exception:
                LOGGER.exception("Failed to execute %s", func.__name__)

        thread = threading.Thread(target=run)
        thread.start()

    return wrapper
