# Licensed under the MIT License.
# pytypex Copyright (C) 2022 numlinka.

__all__ = [
    "Static",
    "Abstract",
    "abstractmethod",
    "Singleton",
    "Multiton",
    "Atomic",
    "AbsoluteAtomic",
    "MultitonAtomic"
]

# std
import sys

from abc import ABC, abstractmethod
from types import MethodType, FunctionType
from typing import Dict, Any, TypeVar, Union
from threading import RLock

# internal
from .constants import *


if sys.version_info >= (3, 11):
    from typing import Self

else:
    Self = object


class Static (object):
    """
    Static class.

    This class cannot be instantiated.
    """
    def __new__(cls):
        raise TypeError("Cannot instantiate static class.")


class Abstract (ABC):
    """
    Abstract class.

    All methods decorated with `abstractmethod` must be rewritten, otherwise they cannot be instantiated.
    """


class Singleton (object):
    """
    Singleton class.

    This class will only be instantiated once to ensure that there is only one instance.
    The `__init__` method of the subclass will be replaced to ensure that the method is only executed once.
    """
    _singleton_instance: Self  # <-- cls
    _singleton_init_method: Union[MethodType, FunctionType]  # <-- cls
    _singleton_initialized: bool  # <-- cls

    def __new__(cls, *args, **kwargs) -> object:
        if cls is Singleton:
            raise TypeError("Cannot instantiate base singleton class.")
        if not hasattr(cls, "_singleton_instance"):
            # In fact, we can directly call the instance's __init__ method in the __new__ phase,
            # and then replace __init__ with an empty function, which can save a lot of things.
            # But I think this is not in line with the norms.
            cls._singleton_init_method = cls.__init__
            cls.__init__ = Singleton.__init__
            cls._singleton_instance = super(Singleton, cls).__new__(cls)
        return cls._singleton_instance

    def __init__(self, *args, **kwargs) -> None:
        cls = self.__class__
        if not hasattr(cls, "_singleton_initialized") or not cls._singleton_initialized:
            cls._singleton_initialized = True
            self._singleton_init_method(*args, **kwargs)


class Multiton (object):
    """
    Multiton pattern class.

    This class can have multiple instances at the same time, and you can create or get them.
    The `__init__` method of the subclass will be replaced to ensure that the method
    is only executed once for each instance.
    """
    _multiton_instances: Dict[str, Self]  # <-- cls
    _multiton_init_method: Union[MethodType, FunctionType]  # <-- cls
    _multiton_initialized: bool  # <-- instance

    def __new__(cls, *args, instance_name: str = DEFAULT, **kwargs) -> Self:
        if cls is Multiton:
            raise TypeError("Cannot instantiate base multiton class.")

        if not hasattr(cls, "_multiton_instances"):
            cls._multiton_instances = dict()

        if instance_name in cls._multiton_instances:
            return cls._multiton_instances[instance_name]

        if not hasattr(cls, "_multiton_init_method"):
            cls._multiton_init_method = cls.__init__
            cls.__init__ = Multiton.__init__

        instance = super(Multiton, cls).__new__(cls)

        cls._multiton_instances[instance_name] = instance
        return instance

    def __init__(self, *args, instance_name: str = DEFAULT, **kwargs) -> None:
        self.__instance_name = instance_name
        if not hasattr(self, "_multiton_initialized") or not self._multiton_initialized:
            self._multiton_initialized = True
            self._multiton_init_method(*args, **kwargs)

    @property
    def instance_name(self) -> str:
        """The name of the instance. | **read-only**"""
        return self.__instance_name

    @classmethod
    def get_instance(cls, instance_name: str, *args: Any, **kwargs: Any) -> Self:
        """
        Get an instance of the class.

        Arguments:
            instance_name (str): The name of the instance.
            *args (Any): The arguments to pass to the constructor.
            **kwargs (Any): The keyword arguments to pass to the constructor.
        """
        return cls(*args, instance_name=instance_name, **kwargs)


class Atomic (object):
    """
    Atomic counter.
    """
    def __init__(self, max_value: int = -1) -> None:
        """
        Initialize the atomic counter.

        Arguments:
            max_value (int): The maximum value of the counter, when exceeded, the count starts again, -1 means no limit.
        """
        self.__lock = RLock()
        self.__count = -1
        self._set_max_value(max_value)

    def _set_max_value(self, max_value: int) -> None:
        with self.__lock:
            if not isinstance(max_value, int):
                raise TypeError("Argument max_value must be an integer.")
            if max_value < -1 or max_value == 0:
                raise ValueError(f"Invalid max_value: {max_value}")
            self.__max_value = max_value

    def get_count(self) -> int:
        with self.__lock:
            self.__count += 1
            if self.__max_value != -1 and self.__count >= self.__max_value:
                self.__count = 0
            return self.__count

    @property
    def count(self) -> int:
        return self.get_count()

    @property
    def value(self) -> int:
        return self.count


class AbsoluteAtomic (Singleton, Atomic):
    """
    Absolute atomic counter.

    This is a singleton class, which means there will be only one instance of this class, and it will share the counter.
    """
    def __init__(self, max_value: int = -1) -> None:
        Atomic.__init__(self, max_value=max_value)


class MultitonAtomic (Multiton, Atomic):
    """
    Multiton atomic counter.

    This is a multiton class, which means that each instance of this class will have its own counter.
    """
    def __init__(self, max_value: int = -1, instance_name: str = DEFAULT, **kwargs) -> None:
        Atomic.__init__(self, max_value=max_value)
