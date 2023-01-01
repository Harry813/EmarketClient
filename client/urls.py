from django.urls import path, re_path

from . import views

app_name = 'client'

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),

    path('product/', views.products_view, name='shop'),
    path('product/<str:product_id>/', views.product_detail_view, name='product'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('pay/<str:order_id>/', views.pay_view, name='pay'),
    path('pay/finish/<str:order_id>/', views.pay_finish, name='pay_finish'),

    re_path(r'login/$', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
