from django.urls import path, include
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('profile/', views.profile_view, name='profile'),
    path('error/', views.error_view, name='error'),
    path('accounts/', include('allauth.urls')),
    
    # Exercise plan URLs
    path('exercise-plans/', views.exercise_plan_list, name='exercise_plan_list'),
    path('exercise-plan/<int:plan_id>/', views.exercise_plan_detail, name='exercise_plan_detail'),
    path('exercise-plan/<int:plan_id>/checkout/', views.create_plan_checkout_session, name='create_plan_checkout_session'),
] 