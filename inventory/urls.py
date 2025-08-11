from django.urls import path, include
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update/<str:item_type>/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:item_type>/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('nutrition-plan/<int:plan_id>/payment-success/', views.nutrition_plan_payment_success, name='nutrition_plan_payment_success'),
    path('exercise-plan/<int:plan_id>/payment-success/', views.exercise_plan_payment_success, name='exercise_plan_payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('profile/', views.profile_view, name='profile'),
    path('error/', views.error_view, name='error'),
    path('accounts/', include('allauth.urls')),
    
    # Exercise plan URLs
    path('exercise-plan/<int:plan_id>/checkout/', views.create_exercise_plan_checkout_session, name='create_exercise_plan_checkout_session'),
    
    # Nutrition Plan URLs
    path('nutrition-plans/', views.nutrition_plan_list, name='nutrition_plan_list'),
    path('nutrition-plan/<int:plan_id>/', views.nutrition_plan_detail, name='nutrition_plan_detail'),
    path('nutrition-plan/<int:plan_id>/checkout/', views.create_plan_checkout_session, name='create_plan_checkout_session'),
    path('nutrition-plan/<int:plan_id>/meal/<int:meal_id>/complete/', views.complete_meal, name='complete_meal'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('facebook-mockup/', views.facebook_mockup, name='facebook_mockup'),
    path('progress/', views.progress_dashboard, name='progress_dashboard'),
    path('set-timezone/', views.set_timezone, name='set_timezone'),
] 