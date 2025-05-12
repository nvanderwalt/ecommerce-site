from django.urls import path
from .views import CreateCheckoutSessionView, success_view, cancel_view

urlpatterns = [
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/<int:order_id>/', success_view, name='checkout_success'),
    path('cancel/<int:order_id>/', cancel_view, name='checkout_cancel'),
]
