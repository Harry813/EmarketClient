from django.urls import path, include

from . import views

app_name = 'kern'

in_site_api = [
    path('wishlist/', views.wishlist_api, name='wishlist'),
    path('cart/', views.cart_api, name='cart'),
    path('cart/checkout/', views.checkout_api, name='checkout'),
    path("user/resetpaswd", views.reset_password, name="reset_password")
]

out_site_api = [
    path('sync/', views.sync_api, name='sync'),
    path('sysinfo/', views.sysinfo_api, name='sysinfo'),
    path('user/resetpaswd', views.reset_password, name='reset_password')
]

urlpatterns = [
    path('api/', include(in_site_api), name='api'),
    path('rmt/', include(out_site_api), name='rmt'),
]
