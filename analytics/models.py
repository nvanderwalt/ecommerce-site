from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class UserActivity(models.Model):
    """Track user activities across the site."""
    ACTIVITY_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('VIEW_PRODUCT', 'View Product'),
        ('ADD_TO_CART', 'Add to Cart'),
        ('REMOVE_FROM_CART', 'Remove from Cart'),
        ('CHECKOUT', 'Checkout'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Generic relation to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data stored as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"

class SiteStatistics(models.Model):
    """Store aggregated site statistics."""
    date = models.DateField(unique=True)
    total_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active_subscriptions = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    cancelled_subscriptions = models.PositiveIntegerField(default=0)
    trial_conversions = models.PositiveIntegerField(default=0)
    
    # Store additional metrics as JSON
    metrics = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = 'Site Statistics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Statistics for {self.date}"

class ProductAnalytics(models.Model):
    """Track product-specific analytics."""
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    add_to_cart = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = 'Product Analytics'
        unique_together = ['product', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.product.name} - {self.date}"

class SubscriptionAnalytics(models.Model):
    """Track subscription-specific analytics."""
    plan = models.ForeignKey('subscriptions.SubscriptionPlan', on_delete=models.CASCADE)
    date = models.DateField()
    active_subscriptions = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    cancellations = models.PositiveIntegerField(default=0)
    renewals = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trial_starts = models.PositiveIntegerField(default=0)
    trial_conversions = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Subscription Analytics'
        unique_together = ['plan', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.plan.name} - {self.date}"
