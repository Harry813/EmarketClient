from django.urls import reverse
from rest_framework import serializers

from .models import *


class CartItemSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(source='variant_id')

    class Meta:
        model = CartItem
        fields = ['id', 'quantity']
