from django.urls import path, include

from . import views

app_name = 'kern'

insite_api = [
    path('wishlist/', views.wishlist_api, name='wishlist'),
    path('cart/', views.cart_api, name='cart'),
    path('cart/checkout/', views.checkout_api, name='checkout'),
]

urlpatterns = [
    path('api/', include(insite_api)),
]
