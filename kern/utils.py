import json
import os

import requests as rq
from django.contrib.auth import authenticate, login

from EmarketClient import settings
from .models import *


def send_request (url, method, data=None, headers=None):
    """
    Send request to url
    :param url: url path to send request (e.g. /path/to/api)
    :param method: request method ["GET", "POST", "PUT", "DELETE"]
    :param data: data to send in format of dictionary, required by POST and PUT
    :param headers: headers to send
    """
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


def create_user(**kwargs):
    """
    Create user with username, password, email, first_name, last_name
    Please check the password format before creation
    """
    username = kwargs.get("username")
    email = kwargs.get("email")
    password = kwargs.get("password")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password)
    response = send_request("/auth/register/", "POST",
                            {"username": username, "email": email,
                             "first_name": first_name, "last_name": last_name})
    if response.status_code == 201:
        user.uuid = response.json()["id"]
        user.save()
        return user
    else:
        return None


def v_record (request):
    data = {
        "ip": request.META["REMOTE_ADDR"],
        "site": request.META["SERVER_NAME"],
        "url": request.path,
        "useragent": request.META["HTTP_USER_AGENT"]
    }
    if request.user.is_authenticated:
        data["user"] = request.user.pk

    UserVisitRecord.objects.create(
        user=request.user if request.user.is_authenticated else None,
        user_agent=request.META["HTTP_USER_AGENT"],
        ip=request.META["REMOTE_ADDR"],
        referer=request.META["HTTP_REFERER"] if "HTTP_REFERER" in request.META else None,
        path=request.path,
        query_string=request.META["QUERY_STRING"],

        site=request.META["SERVER_NAME"],

        method=request.method,
    )


def get_client_params ():
    return {
        "brand": os.getenv("BRAND"),
    }


def glob_id_generator (instance):
    return f"{os.getenv('URL')}@{instance.__class__.__name__}:{str(instance.pk)}"
