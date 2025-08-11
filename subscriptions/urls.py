from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionPlanListView.as_view(), name='plan_list'),
    path('<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='plan_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-subscription/', views.UserSubscriptionView.as_view(), name='user_subscription'),
    path('create/<int:plan_id>/', views.create_subscription, name='create'),
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.subscription_cancel, name='cancel'),
    path('renew/', views.subscription_renew, name='renew'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('download-invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
    path('start-trial/<int:plan_id>/', views.start_trial, name='start_trial'),
    path('convert-trial/<int:subscription_id>/', views.convert_trial, name='convert_trial'),
    path('switch-plan/<int:plan_id>/', views.switch_subscription_plan, name='switch_plan'),
    path('toggle-auto-renew/<int:subscription_id>/', views.toggle_auto_renew, name='toggle_auto_renew'),
] 