import logging

from dotenv import load_dotenv

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

import EmarketClient.settings
from client.forms import *
from kern.models import *
from kern.utils.auth import login_user, create_user
from kern.utils.core import send_request
from kern.utils.utils import *

load_dotenv(verbose=True)


def index (request):
    return redirect("client:shop")
    # params = {
    #     "active_page": "index",
    #     **get_client_params(request=request, page_title=_("首页")),
    # }
    # return render(request, 'client/index.html', params)


# def test (request):
#     if not EmarketClient.settings.DEBUG:
#         return HttpResponse(status=403)
#     response = send_request("/auth/register/", "POST",
#                             {"username": "TestUser", "email": "test@test.com",
#                              "first_name": "Test", "last_name": "User"})
#     return HttpResponse(response)


def login_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("登录")),
    }
    try:
        next_url = request.GET.get("next")
    except IndexError:
        next_url = reverse("mgt:index")

    if request.user.is_authenticated:
        return HttpResponseRedirect(next_url)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            paswd = form.cleaned_data.get("password")

            try:
                login_user(request=request, username=username, password=paswd)
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return redirect("client:index")
            except ValueError as e:
                form.add_error(None, ValidationError(e, code="LoginFailed"))
        else:
            form = LoginForm(request.POST)
    else:
        form = LoginForm()

    param["form"] = form
    return render(request, 'client/login.html', param)


def logout_view (request):
    logout(request)
    return redirect("client:index")


def register_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("注册")),
    }
    invitor = request.GET.get("ref", None)
    param["ref"] = invitor

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = create_user(
                username=form.cleaned_data.get("username"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
                first_name=form.cleaned_data.get("first_name"),
                last_name=form.cleaned_data.get("last_name"),
                invitor=invitor if invitor else form.cleaned_data.get("invitor"),
            )
            if user:
                login(request, user)
                return redirect("client:index")
            else:
                form.add_error(None, ValidationError(_("注册失败，请重试"), code="RegisterFailed"))
        else:
            form.add_error(None, ValidationError("测试1", code="RegisterFailed"))
    else:
        form = RegisterForm()

    param["form"] = form
    return render(request, 'client/register.html', param)


def products_view (request):
    param = {
        "active_page": "shop",
        **get_client_params(request=request, page_title=_("产品")),
    }
    page = request.GET.get("page", 1)

    products = Product.objects.all()
    p = Paginator(products, 12)
    param["products"] = p.get_page(page)
    param["pages"] = p.get_elided_page_range(page, on_each_side=2, on_ends=1)
    param["paginator"] = p
    param["current_page"] = page
    return render(request, 'client/shop.html', param)


def product_detail_view (request, product_id):
    param = {
        "active_page": "shop",
        **get_client_params(request=request, page_title=_("产品")),
    }
    product = get_object_or_404(Product, id=product_id)
    param["product"] = product
    param["imgThumbs"] = zip(product.images)
    return render(request, 'client/product.html', param)


@login_required(login_url="client:login")
def wishlist_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("心愿单")),
    }
    user = User.objects.get(id=request.user.id)
    param["wishlist"] = user.wishlist.all()
    return render(request, 'client/wishlist.html', param)


@login_required(login_url="client:login")
def cart_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("购物车")),
    }
    return render(request, 'client/cart.html', param)


@login_required(login_url="client:login")
def checkout_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("结账")),
    }

    # todo: 用户信息、地址自动填充
    u = User.objects.get(id=request.user.id)
    form_default_data = {
        "billing_first_name": u.first_name,
        "billing_last_name": u.last_name,
    }

    order_id = request.GET.get("id", None)
    if order_id:
        order = Order.objects.get(id=order_id)
    else:
        order = Order.objects.get(user=request.user, is_active=True)
    order.update()

    param["order"] = order

    if request.method == "POST":
        form = CheckoutForm(request.POST, initial=form_default_data)
        if form.is_valid():
            data = {
                "first_name": form.cleaned_data.get("billing_first_name"),
                "last_name": form.cleaned_data.get("billing_last_name"),
                "phone": form.cleaned_data.get("billing_phone"),
                "address_line1": form.cleaned_data.get("billing_address_line1"),
                "address_line2": form.cleaned_data.get("billing_address_line2"),
                "city": form.cleaned_data.get("billing_city"),
                "state": form.cleaned_data.get("billing_state"),
                "country": form.cleaned_data.get("billing_country"),
                "zip_code": form.cleaned_data.get("billing_zip_code"),
                "customer": str(request.user.id),
            }

            response = send_request("/address/", "POST", data)

            if response.status_code in [200, 201]:
                billing_address_id = response.json().get("id")
                billing_address, is_created = Address.objects.get_or_create(id=billing_address_id)
                billing_address.update()
            else:
                form.add_error(None, ValidationError(response.text, code="CheckoutFailed"))
                param["form"] = form
                return render(request, 'client/checkout.html', param)

            shipping_address_id = None
            if form.cleaned_data["ship_to_different_address"]:
                data = {
                    "first_name": form.cleaned_data.get("shipping_first_name"),
                    "last_name": form.cleaned_data.get("shipping_last_name"),
                    "phone": form.cleaned_data.get("shipping_phone"),
                    "address_line1": form.cleaned_data.get("shipping_address_line1"),
                    "address_line2": form.cleaned_data.get("shipping_address_line2"),
                    "city": form.cleaned_data.get("shipping_city"),
                    "state": form.cleaned_data.get("shipping_state"),
                    "country": form.cleaned_data.get("shipping_country"),
                    "zip_code": form.cleaned_data.get("shipping_zip_code"),
                    "customer": str(request.user.id),
                }
                response = send_request("/address/", "POST", data)
                if response.status_code in [200, 201]:
                    shipping_address_id = response.json().get("id")
                    shipping_address, is_created = Address.objects.get_or_create(id=shipping_address_id)
                    shipping_address.update()
                else:
                    form.add_error(None, ValidationError(_("寄送地址验证失败，请重试"), code="CheckoutFailed"))
                    param["form"] = form
                    return render(request, 'client/checkout.html', param)

            data = {
                "order": order.id,
                "payment_method": form.cleaned_data.get("payment_method"),
                "billing_address": billing_address_id,
                "shipping_address": shipping_address_id,
                "amount": order.total,
                "currency": "GBP",
            }
            response = send_request("/pay/", "POST", data)
            if response.status_code == 200:
                return redirect("client:pay", order_id=order.id)
            else:
                form.add_error(None, "信息拉取失败，请稍后重试")
        else:
            form = CheckoutForm(request.POST, initial=form_default_data)
    else:
        form = CheckoutForm(initial=form_default_data)

    param["form"] = form
    return render(request, 'client/checkout.html', param)


@login_required(login_url="client:login")
def pay_view (request, order_id):
    param = {
        "active_page": "user",
        "order_id": order_id,
        **get_client_params(request=request, page_title=_("支付")),
    }

    order = get_object_or_404(Order, id=order_id, user=request.user)
    # todo: 检查订单状态，并执行相应跳转
    order.update()
    response = send_request("/pay/", "GET", {"id": order.id, "mode": "pay"})
    if response.status_code == 200:
        param.update(response.json())
    else:
        return HttpResponseBadRequest(response)
    return render(request, 'client/payment.html', param)


@login_required(login_url="client:login")
def pay_finish (request, order_id):
    u = User.objects.get(id=request.user.id)

    response = send_request("/pay/", "GET", {"id": order_id, "mode": "finish"})
    if response.status_code == 200:
        Order.objects.get(id=order_id).update()
        CartItem.objects.filter(user=u).delete()
        return redirect("client:order", order_id=order_id)
    else:
        return HttpResponseBadRequest(response)


@login_required(login_url="client:login")
def profile_view (request):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("个人信息")),
    }

    u = User.objects.get(id=request.user.id)
    orders = Order.objects.filter(user=u, )
    param["orders"] = orders
    param["invitation_url"] = request.build_absolute_uri(reverse("client:register")) + "?ref=" + str(u.id)

    return render(request, 'client/profile.html', param)


@login_required(login_url="client:login")
def order_view (request, order_id):
    param = {
        "active_page": "user",
        **get_client_params(request=request, page_title=_("订单详情")),
    }

    u = User.objects.get(id=request.user.id)
    order = get_object_or_404(Order, id=order_id, user=u)
    order.update()
    if order.status == "CREATED":
        return HttpResponseRedirect(reverse("client:checkout") + "?id=" + str(order.id))
    param["order"] = order
    return render(request, 'client/order.html', param)
