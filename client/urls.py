from django.urls import path, re_path

from . import views

app_name = 'client'

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),

    re_path(r'login/$', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
