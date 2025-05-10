from django.urls import path
from .views import post_list, post_create

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new/', post_create, name='post_create'),
]
