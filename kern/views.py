import json

from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *
from rest_framework.response import Response

from kern.models import *


@csrf_exempt
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def wishlist_api (request, format=None):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.pk)
        variant_id = request.data.get("id")
        obj, status = WishlistItem.objects.get_or_create(user=user, variant_id=variant_id)
        if not status:
            return Response({"msg": _("该物品已在心愿单中")}, status=HTTP_200_OK)
        return Response({"msg": _("添加成功")}, status=HTTP_201_CREATED)
    elif request.method == "DELETE":
        user = User.objects.get(pk=request.user.pk)
        variant_id = request.query_params.get("id")
        if variant_id is None:
            return Response({"ERR": "No variant id provided"}, status=HTTP_400_BAD_REQUEST)
        WishlistItem.objects.filter(user=user, variant_id=variant_id).delete()
        return Response({"msg": _('删除成功，1.5秒后刷新页面')}, status=HTTP_200_OK)


@csrf_exempt
@api_view(['GET', 'POST', 'PUSH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_api (request):
    if request.method == "GET":
        items = CartItem.objects.filter(user=request.user)
        total_price = sum([item.variant.price * item.quantity for item in items])
        return Response({"items": items, "total_price": total_price}, status=HTTP_200_OK)
    elif request.method == "POST":
        user = User.objects.get(pk=request.user.pk)
        variant_id = request.data.get("id", None)
        quantity = request.data.get("quantity", 1)
        obj, is_created = CartItem.objects.get_or_create(user=user, variant_id=variant_id)
        if not is_created:
            obj.quantity += quantity
            obj.save()
            return Response({"msg": _("商品添加成功，购物车中有 %(count)s 件") % {'count': obj.quantity}},
                            status=HTTP_200_OK)
        return Response({"msg": _("添加成功")}, status=HTTP_201_CREATED)
    elif request.method == "PUSH":
        user = User.objects.get(pk=request.user.pk)
        mode = request.data.get("mode", None)
        if mode == "full_update":
            items = request.data.get("items", None)
            if items is None:
                return Response({"msg": _("无效的请求")}, status=HTTP_400_BAD_REQUEST)
            items = json.loads(items)
            for item in items:
                variant_id = item.get("id", None)
                quantity = item.get("quantity", None)
                if variant_id is None or quantity is None:
                    return Response({"msg": _("无效的请求")}, status=HTTP_400_BAD_REQUEST)

                obj, status = CartItem.objects.get_or_create(user=user, variant_id=variant_id)
                if not status:
                    obj.quantity = quantity
                    obj.save()
            return Response({"msg": _("更新成功, 1.5秒后将刷新页面")}, status=HTTP_200_OK)
        else:
            variant_id = request.data.get("variants")
            quantity = request.data.get("quantity")
            obj, status = CartItem.objects.get_or_create(user=user, variant_id=variant_id)
            if not status:
                obj.quantity = quantity
                obj.save()
                return Response({"msg": _("商品修改成功, 1.5秒后将刷新页面") % {'count': obj.quantity}},
                                status=HTTP_200_OK)
        return Response({"ERR": "Unknown err"}, status=HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        user = User.objects.get(pk=request.user.pk)
        variant_id = request.query_params.get("id")
        if variant_id is None:
            return Response({"ERR": _("无效的请求")}, status=HTTP_400_BAD_REQUEST)
        CartItem.objects.filter(user=user, variant_id=variant_id).delete()
        return Response({"msg": _('删除成功，1.5秒后刷新页面')}, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_api (request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.pk)

        items = request.data.get("items", None)
        if not items:
            return Response({"msg": _("无效的请求")}, status=HTTP_400_BAD_REQUEST)
        for item in items:
            variant_id = item.get("id", None)
            quantity = item.get("quantity", None)
            if variant_id is None or quantity is None:
                return Response({"msg": _("无效的请求")}, status=HTTP_400_BAD_REQUEST)

            obj, is_created = CartItem.objects.get_or_create(user=user, variant_id=variant_id)
            if not is_created:
                obj.quantity = int(quantity)
                obj.save()

        coupon = request.data.get("coupon", "")
        if coupon != "":
            response = send_request("/coupon/validate/", "GET", {"code": coupon})
            if response.status_code != 200:
                return Response({"msg": _("优惠券无效")}, status=HTTP_400_BAD_REQUEST)

        items = [{"id": str(item.variant_id), "quantity": item.quantity} for item in CartItem.objects.filter(user=user)]
        payload = {
            "user": str(User.objects.get(pk=request.user.pk).id),
            "items": items,
            "coupon": coupon,
        }

        response = send_request('/checkout/', "POST", payload, is_json=True)
        if response.status_code == 200:
            order_id = response.json().get("id", None)
            Order.objects.get_or_create(id=order_id, user=user, is_active=True)
            return Response({"id": order_id}, status=HTTP_200_OK)
        else:
            return Response({"msg": response.text}, status=HTTP_400_BAD_REQUEST)
