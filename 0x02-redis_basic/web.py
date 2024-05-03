#!/usr/bin/env python3
""" implements a get_page function (prototype: def get_page(url: str) -> str:)
    The core of the function is very simple. It uses the requests module to
    obtain the HTML content of a particular URL and returns it.

    get_page tracks how many times a particular URL was accessed in the key
    "count:{url}" and cache the respult with an expiration time of 10 seconds.

    Bonus: implement this use case with decorators.
"""
import redis
import requests
from typing import Callable
from functools import wraps

count = 0
cache = redis.Redis()


def get_page(url: str) -> str:
    """Obtains the HTML content of a particular URL and returns it.
    Tracks how many times the URL was accessed and storesp this
    count in a Redis cache.
    """
    cache.set(f"cached:{url}", count)
    response = requests.get(url)
    cache.incr(f"count:{url}")
    cache.setex(f"count:{url}", 10, cache.get(f"cached:{url}"))
    return response.text
