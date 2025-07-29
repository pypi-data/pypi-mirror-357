import time

import requests


def get_page(url: str, method: str = "get") -> requests.Response:
    """Request `url` and return the `requests.Response` object."""
    try:
        return requests.request(method, url, timeout=30)
    except Exception as e:
        time.sleep(1)
        return requests.request(method, url, timeout=30)
