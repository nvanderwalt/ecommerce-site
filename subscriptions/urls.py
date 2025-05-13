from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='plan_detail'),
    path('my-subscription/', views.UserSubscriptionView.as_view(), name='user_subscription'),
] 