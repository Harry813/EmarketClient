import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from client.forms import *
from kern.utils import *


# Create your views here.
def index (request):
    params = {
        **get_client_params(),
    }
    v_record(request)
    return render(request, 'client/index.html', params)


def test (request):
    r = send_request("/auth/site/validate/", "POST", {"ip": os.getenv("IPv4")})
    if r.status_code == 200:
        return HttpResponse("Success")
    else:
        return HttpResponse(r)


def login_view (request):
    param = {
        **get_client_params(),
    }
    v_record(request)
    try:
        next_url = request.POST.get("next")
    except IndexError:
        next_url = reverse("mgt:index")

    if request.user.is_authenticated:
        return HttpResponseRedirect(next_url)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            paswd = form.cleaned_data.get("password")

            user = authenticate(
                request=request,
                username=username,
                password=paswd
            )
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    if next_url:
                        return HttpResponseRedirect(next_url)
                    else:
                        return redirect("client:index")
                else:
                    raise PermissionDenied
            else:
                form.add_error(None, ValidationError(_("用户不存在"), code="UserNotExist"))
        else:
            form = LoginForm(request.POST)
    else:
        form = LoginForm()

    param["form"] = form
    return render(request, 'client/login.html', param)
