from django.urls import path
from .views import CreateCheckoutSessionView

urlpatterns = [
    path('buy/<int:pk>/', CreateCheckoutSessionView.as_view(), name='buy'),
]
