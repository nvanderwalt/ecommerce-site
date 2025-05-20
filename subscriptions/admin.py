from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'stripe_subscription_id'
    )
    list_filter = ('status', 'auto_renew', 'plan', 'end_date')
    search_fields = ('user__email', 'plan__name', 'stripe_subscription_id')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
