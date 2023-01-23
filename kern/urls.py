from django.urls import path, include

from . import views

app_name = 'kern'

in_site_api = [
    path('wishlist/', views.wishlist_api, name='wishlist'),
    path('cart/', views.cart_api, name='cart'),
    path('cart/checkout/', views.checkout_api, name='checkout'),
]

out_site_api = [
    path('sync/', views.sync_api, name='sync'),
]

urlpatterns = [
    path('api/', include(in_site_api)),
    path('rem/', include(out_site_api)),
]
