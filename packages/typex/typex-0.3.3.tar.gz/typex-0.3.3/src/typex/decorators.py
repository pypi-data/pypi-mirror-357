# Licensed under the MIT License.
# pytypex Copyright (C) 2022 numlinka.

__all__ = [
    "mutex",
    "once"
]

# std
import threading
from typing import Callable


def mutex(func: Callable):
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper


def once(func):
    lock = threading.Lock()
    executed = False

    def wrapper(*args, **kwargs):
        nonlocal executed
        if executed:
            raise RuntimeError(f"Function '{func.__name__}' can only be called once.")

        with lock:
            if executed:
                raise RuntimeError(f"Function '{func.__name__}' can only be called once.")

            executed = True
            return func(*args, **kwargs)

    return wrapper
