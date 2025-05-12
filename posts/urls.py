from django.urls import path
from . import views

urlpatterns = [
    path('edit/<int:post_id>/', views.post_edit, name='post_edit'),
    path('delete/<int:post_id>/', views.post_delete, name='post_delete'),
]