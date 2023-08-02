import datetime
import logging
import uuid

from django.contrib.auth import authenticate, login
from requests import HTTPError

from kern.models import User, generate_invitation_code
from kern.utils.core import send_request


def v_record (request):
    ip = request.headers.get("X-Forwarded-For", None)
    if not ip:
        ip = request.META.get("REMOTE_ADDR", None)

    if ip:
        response = send_request("/whitelist/", "GET", payload={"ip": ip})
        if response.status_code == 204:
            send_request("/visit/", "POST", {
                "customer": request.user.id if request.user.is_authenticated else None,
                "user_agent": request.META.get("HTTP_USER_AGENT", None),
                "visited_at": datetime.datetime.now(),
                "ip": ip,
                "referer": request.META.get("HTTP_REFERER", None),
                "path": request.path,
                "query_string": request.META.get("QUERY_STRING", None),
                "method": request.method,
            })


def create_user(**kwargs):
    """
    Create user with username, password, email, first_name, last_name
    Please check the password format before creation
    """
    logging.info(f"Creating user: {kwargs}")
    password = kwargs.pop("password")
    invitor = kwargs.pop("invitor", "")

    invitation_code = generate_invitation_code()
    response = send_request("/auth/register/", "POST",
                            {
                                "invitor": invitor if invitor else "",
                                "invitation_code": invitation_code,
                                **kwargs
                            })
    try:
        response.raise_for_status()
        if response.status_code == 201:
            user = User.objects.create(
                id=uuid.UUID(response.json()["id"]),
                invitation_code=invitation_code,
                **kwargs
            )
            user.set_password(password)
            user.save()
            return user
        else:
            raise HTTPError()
    except HTTPError:
        logging.error(f"ERR: {response.status_code}: {response.text}")
        return None


def login_user (request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        response = send_request("/auth/login/", "POST", {"id": str(user.id)})
        if response.status_code == 200:
            login(request, user)
        else:
            raise ValueError(response.json()["detail"])
    else:
        raise ValueError("User not found")
