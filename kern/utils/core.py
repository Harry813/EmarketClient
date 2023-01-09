import json
import os

import requests as rq

from EmarketClient import settings


def send_request (url, method, payload=None, headers=None, is_json=False):
    """
    Send request to url
    """
    method = method.upper()
    if headers is None:
        headers = {}
    headers = {
        "X-Api-Key": os.getenv("API_KEY"),
        **headers
    }

    url = f"{settings.API_ROOT}{url}"

    if method == "GET":
        return rq.get(url, headers=headers, params=payload)
    elif method == "POST":
        if is_json:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(payload)
        return rq.post(url, data=payload, headers=headers)
    elif method == "PUT":
        if is_json:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(payload)
        return rq.put(url, data=payload, headers=headers)
    elif method == "DELETE":
        return rq.delete(url, headers=headers, params=payload)
    else:
        return None
