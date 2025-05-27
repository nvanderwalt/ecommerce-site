from django.contrib import admin
from .models import UserActivity, SiteStatistics, ProductAnalytics, SubscriptionAnalytics

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

@admin.register(SiteStatistics)
class SiteStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'total_orders', 'total_revenue')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('date',)

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'views', 'add_to_cart', 'purchases', 'revenue')
    list_filter = ('date', 'product')
    search_fields = ('product__name',)
    date_hierarchy = 'date'
    readonly_fields = ('date',)

@admin.register(SubscriptionAnalytics)
class SubscriptionAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('plan', 'date', 'active_subscriptions', 'new_subscriptions', 'revenue')
    list_filter = ('date', 'plan')
    search_fields = ('plan__name',)
    date_hierarchy = 'date'
    readonly_fields = ('date',)
