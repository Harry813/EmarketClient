from django.urls import path, re_path

from . import views

app_name = 'client'

urlpatterns = [
    path('', views.test, name='test'),
]
