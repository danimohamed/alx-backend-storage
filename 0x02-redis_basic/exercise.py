#!/usr/bin/env python3
"""Writing strings to Redis"""

from functools import wraps
import redis
from typing import Any, Callable, Optional, Union
from uuid import uuid4


def call_history(method: Callable) -> Callable:
    """
    decorator to store the history of inputs
    and outputs for a particular function
    """

    input = method.__qualname__ + ':inputs'
    output = method.__qualname__ + ':outputs'

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """
        use rpush to append the input arguments.
        use rpush to  Store the output.
        return the output.
        """
        self._redis.rpush(input, str(args))
        res = method(self, *args)
        self._redis.rpush(output, res)
        return res
    return wrapper


def count_calls(method: Callable) -> Callable:
    """
    decorator that takes a single method Callable
    argument and returns a Callable
    """
    key = method.__qualname__
    # print("qualified name", key) // Cache.store

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """
        wrapper fn that increments the count for that key every
        time the method is called and returns the value returned
        by the original method
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def replay(method: Callable) -> None:
    """display the history of calls of a particular function
    """
    key = method.__qualname__
    data = redis.Redis()
    hist = data.get(key).decode("utf-8")
    print("{} was called {} times:".format(key, hist))
    inputs = data.lrange(key + ":inputs", 0, -1)
    outputs = data.lrange(key + ":outputs", 0, -1)
    for k, v in zip(inputs, outputs):
        print(f"{key}(*{k.decode('utf-8')}) -> {v.decode('utf-8')}")


class Cache:
    """ Class for redis cache """
    def __init__(self):
        """constructor for redis cache"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        takes a data argument and returns a string
        generates a random key using uuid from stored input data
        stores the input data in Redis using the random key
        returns the key
        """

        key = str(uuid4())
        self._redis.mset({key: data})
        # print(self._redis.get(key))
        return key

    def get(
            self, key: str, fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        """converts the data back to the desired format

        Args:
            key (str): string argument
            fn (Optional[Callable], optional): will be
                        used to convert the
                        data back to the desired format..
                        Defaults to None.
        Returns:
            Any: string, bytes and numbers (and lists thereof)
        """
        _bytes = self._redis.get(key)
        return fn(_bytes) if fn else _bytes

    def get_str(self, key: str) -> str:
        """parametize get with string"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """parametize get with int"""
        return self.get(key, int)
