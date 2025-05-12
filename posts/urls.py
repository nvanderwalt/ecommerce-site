from django.urls import path
from .views import post_list, post_create, post_delete, post_edit

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new/', post_create, name='post_create'),
    path('edit/<int:post_id>/', post_edit, name='post_edit'),
    path('delete/<int:post_id>/', post_delete, name='post_delete'),
]