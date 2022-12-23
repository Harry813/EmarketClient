import os

import requests as rq

from EmarketClient import settings


def send_request (url, method, data=None, headers=None):
    """
    Send request to url
    :param url: url path to send request (e.g. /path/to/api)
    :param method: request method ["GET", "POST", "PUT", "DELETE"], case insensitive
    :param data: data to send in format of dictionary, required by POST and PUT
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
    # data = json.dumps(data)

    if method == "GET":
        return rq.get(url, headers=headers)
    elif method == "POST":
        return rq.post(url, data=data, headers=headers)
    elif method == "PUT":
        return rq.put(url, data=data, headers=headers)
    elif method == "DELETE":
        return rq.delete(url, headers=headers)
    else:
        return None
