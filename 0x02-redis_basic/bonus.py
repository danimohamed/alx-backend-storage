#!/usr/bin/env python3

import requests
import time
from functools import lru_cache


# Dictionary to track URL accesses
url_access_count = {}


# Decorator to cache results and track URL accesses
def cache_and_track(func):
    @lru_cache(maxsize=100)
    def wrapper(url):
        # Make the request to the URL and fetch the content
        response = requests.get(url)
        page_content = response.text

        # Update the URL access count
        url_access_count[url] = url_access_count.get(url, 0) + 1

        time.sleep(10)  # Simulate slow response

        return page_content

    return wrapper


# Function to get the page content (decorated with cache_and_track)
@cache_and_track
def get_page(url: str) -> str:
    return url


# Example usage
if __name__ == "__main__":
    url_ = "http://slowwly.robertomurray.co.uk/delay/1000/url/"
    url = f"{url_}http://www.google.com"
    print(get_page(url))
    print(get_page(url))
    print(f"Access count for {url}: {url_access_count[url]}")
