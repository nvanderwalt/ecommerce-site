from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'duration_months', 'is_active')
    list_filter = ('plan_type', 'is_active', 'duration_months')
    search_fields = ('name', 'description')
    ordering = ('price',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'is_auto_renewal')
    list_filter = ('status', 'is_auto_renewal', 'plan')
    search_fields = ('user__username', 'user__email', 'stripe_subscription_id')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
