from django.shortcuts import render
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
        return Response({"msg": _('删除成功，2秒后刷新页面')}, status=HTTP_200_OK)
