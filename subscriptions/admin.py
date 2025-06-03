from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, PaymentRecord, TrialUsageStats

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'duration_months', 'price', 'is_active')
    list_filter = ('is_active', 'plan_type')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'is_active')
    list_filter = ('status', 'is_trial', 'auto_renew')
    search_fields = ('user__username', 'user__email', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'plan')

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'subscription', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('invoice_number', 'subscription__user__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('subscription',)

@admin.register(TrialUsageStats)
class TrialUsageStatsAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'last_active', 'conversion_date')
    list_filter = ('last_active', 'conversion_date')
    search_fields = ('subscription__user__email',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('subscription',)
