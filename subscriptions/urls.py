from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionPlanListView.as_view(), name='plan_list'),
    path('<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='plan_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/<int:plan_id>/', views.create_subscription, name='create'),
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.subscription_cancel, name='cancel'),
    path('renew/', views.subscription_renew, name='renew'),
] 