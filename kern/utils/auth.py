from django.contrib.auth import authenticate, login

from kern.models import UserVisitRecord, User
from kern.utils.core import send_request


def v_record (request):
    ip = request.headers.get("X-Forwarded-For", None)
    if not ip:
        ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
    UserVisitRecord.objects.create(
        user=request.user if request.user.is_authenticated else None,
        user_agent=request.META.get("HTTP_USER_AGENT", None),
        session_key=request.session.session_key,
        ip=ip,
        referer=request.META.get("HTTP_REFERER", None),
        path=request.path,
        query_string=request.META.get("QUERY_STRING", None),
        method=request.method,
    )


def create_user (**kwargs):
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
                            data={"username": username, "email": email,
                                  "first_name": first_name, "last_name": last_name})
    if response.status_code == 201:
        user.uuid = response.json()["id"]
        user.save()
        return user
    else:
        return None


def login_user (request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        response = send_request("/auth/login/", "POST", {"id": str(user.uuid)})
        if response.status_code == 200:
            login(request, user)
            return user
        else:
            return None
    else:
        return None
