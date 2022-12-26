from django.urls import path, include

from . import views

app_name = 'kern'

insite_api = [
    path('wishlist/', views.wishlist_api, name='wishlist'),
]

urlpatterns = [
    path('api/', include(insite_api)),
]
