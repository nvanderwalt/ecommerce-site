from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import (
    product_list,
    add_to_cart,
    cart_view,
    register,
    create_checkout_session,
    payment_success,
    profile_view,
    payment_cancel,
    error_view,  # Only import your custom view if you're using it
    update_cart,
    remove_from_cart,  # Add these imports
    exercise_plan_list,
    exercise_plan_detail,
    create_plan_checkout_session,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_list, name='product_list'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('register/', register, name='register'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
    path('profile/', profile_view, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('post/', include('posts.urls')),  # Changed from posts/ to post/ for consistency
    path('checkout/', include('checkout.urls')),
    path('error/', error_view, name='error'),  # ✅ Only this one
    path('update-cart/<int:product_id>/', update_cart, name='update_cart'),  # Add these URLs
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('exercise-plans/', exercise_plan_list, name='exercise_plan_list'),
    path('exercise-plan/<int:plan_id>/', exercise_plan_detail, name='exercise_plan_detail'),
    path('create-plan-checkout-session/<int:plan_id>/', create_plan_checkout_session, name='create_plan_checkout_session'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
