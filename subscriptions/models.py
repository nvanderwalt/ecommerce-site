from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('PRO', 'Professional'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    features = models.JSONField(default=list)  # Store features as a JSON array
    duration_months = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)  # Stripe price ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_plan_type_display()}"

    class Meta:
        ordering = ['price']

class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    is_auto_renewal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plan.name} Subscription"

    def is_active(self):
        now = timezone.now()
        return (
            self.status == 'ACTIVE' and
            self.start_date <= now and
            self.end_date > now
        )

    def cancel_subscription(self):
        self.status = 'CANCELLED'
        self.is_auto_renewal = False
        self.save()

    class Meta:
        ordering = ['-created_at']
