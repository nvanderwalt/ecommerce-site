from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plan_list, name='plan_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/<int:plan_id>/', views.create_subscription, name='create'),
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.subscription_cancel, name='cancel'),
    path('renew/', views.subscription_renew, name='renew'),
] 