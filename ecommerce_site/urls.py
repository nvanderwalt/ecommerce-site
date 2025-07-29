from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import (
    StaticViewSitemap,
    ProductSitemap,
    ExercisePlanSitemap,
    NutritionPlanSitemap,
    PostSitemap,
)
from .views import robots_txt
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
from .views import home_view

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'exercise_plans': ExercisePlanSitemap,
    'nutrition_plans': NutritionPlanSitemap,
    'posts': PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('products/', product_list, name='product_list'),
    path('cart/', cart_view, name='cart'),
    path('register/', register, name='register'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
    path('profile/', profile_view, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('post/', include('posts.urls')),  # Changed from posts/ to post/ for consistency
    path('checkout/', include('checkout.urls')),
    path('error/', error_view, name='error'),  # ✅ Only this one
    path('exercise-plans/', exercise_plan_list, name='exercise_plan_list'),
    path('exercise-plan/<int:plan_id>/', exercise_plan_detail, name='exercise_plan_detail'),
    path('create-plan-checkout-session/<int:plan_id>/', create_plan_checkout_session, name='create_plan_checkout_session'),
    path('subscriptions/', include('subscriptions.urls')),  # Add subscription URLs
    path('inventory/', include('inventory.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/logout/', include('django.contrib.auth.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
