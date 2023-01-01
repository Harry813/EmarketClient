import json
import os

import requests as rq

from EmarketClient import settings


def send_request (url, method, headers=None, is_json=False, **kwargs):
    """
    Send request to url
    :param is_json:
    :param url: url path to send request (e.g. /path/to/api)
    :param method: request method ["GET", "POST", "PUT", "DELETE"], case insensitive
    :param headers: headers to send
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
        params = kwargs.get("params", None)
        return rq.get(url, headers=headers, params=params)
    elif method == "POST":
        data = kwargs.get("data")
        if is_json:
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        return rq.post(url, data=data, headers=headers)
    elif method == "PUT":
        data = kwargs.get("data")
        if is_json:
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        return rq.put(url, data=data, headers=headers)
    elif method == "DELETE":
        params = kwargs.get("params", None)
        return rq.delete(url, headers=headers, params=params)
    else:
        return None
