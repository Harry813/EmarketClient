from django.contrib.auth import logout, login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from client.forms import *
from kern.models import Product
from kern.utils.auth import v_record, create_user, login_user
from kern.utils.content import sync_products
from kern.utils.utils import *


def index (request):
    params = {
        **get_client_params(page_title=_("首页")),
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
        **get_client_params(page_title=_("登录")),
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

            user = login_user(request=request, username=username, password=paswd)
            if user:
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return redirect("client:index")
            else:
                form.add_error(None, ValidationError(_("用户不存在"), code="UserNotExist"))
        else:
            form = LoginForm(request.POST)
    else:
        form = LoginForm()

    param["form"] = form
    return render(request, 'client/login.html', param)


def logout_view (request):
    v_record(request)
    logout(request)
    return redirect("client:index")


def register_view (request):
    param = {
        **get_client_params(page_title=_("注册")),
    }
    v_record(request)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = create_user(
                username=form.cleaned_data.get("username"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
                first_name=form.cleaned_data.get("first_name"),
                last_name=form.cleaned_data.get("last_name"),
            )
            if user:
                login(request, user)
                return redirect("client:index")
            else:
                form.add_error(None, ValidationError(_("注册失败，请重试"), code="RegisterFailed"))
        else:
            form = RegisterForm(request.POST)
    else:
        form = RegisterForm()

    param["form"] = form
    return render(request, 'client/register.html', param)
