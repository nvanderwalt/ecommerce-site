from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='plan_detail'),
    path('my-subscription/', views.UserSubscriptionView.as_view(), name='user_subscription'),
    path('create-checkout-session/<int:plan_id>/', views.create_subscription_checkout, name='create_checkout_session'),
    path('switch-plan/<int:plan_id>/', views.switch_subscription_plan, name='switch_plan'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('dashboard/', views.dashboard, name='subscription_dashboard'),
] 