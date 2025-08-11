from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import stripe
from django.conf import settings
import logging
import random
import string
from django.core.validators import MinValueValidator
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

class SubscriptionPlan(models.Model):
    """
    Represents a subscription plan that users can subscribe to.
    Each plan has specific features, duration, and pricing.
    """
    name = models.CharField(max_length=100)
    plan_type = models.CharField(
        max_length=10,
        choices=[
            ('BASIC', 'Basic'),
            ('PREMIUM', 'Premium'),
            ('PRO', 'Professional')
        ]
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField(default=1)
    features = models.JSONField(default=list)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return self.name

    def get_features_list(self):
        return json.loads(self.features) if isinstance(self.features, str) else self.features

class UserSubscription(models.Model):
    """
    Represents a user's subscription to a specific plan.
    Tracks the subscription status, duration, and renewal settings.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('PENDING_RENEWAL', 'Pending Renewal'),
        ('TRIAL', 'Trial')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    trial_end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_active(self):
        is_active = self.status == 'ACTIVE' and self.end_date > timezone.now()
        print(f"DEBUG: UserSubscription {self.id} is_active check:")
        print(f"  - status: {self.status}")
        print(f"  - end_date: {self.end_date}")
        print(f"  - current_time: {timezone.now()}")
        print(f"  - end_date > current_time: {self.end_date > timezone.now()}")
        print(f"  - is_active result: {is_active}")
        return is_active

    @property
    def can_renew(self):
        return self.status == 'CANCELLED' and self.end_date > timezone.now()

    def get_remaining_days(self):
        if not self.is_active:
            return 0
        remaining = self.end_date - timezone.now()
        return max(0, remaining.days)

    def get_progress_percentage(self):
        if not self.is_active:
            return 100
        total_days = (self.end_date - self.start_date).days
        remaining_days = self.get_remaining_days()
        return int(((total_days - remaining_days) / total_days) * 100)

    def cancel(self):
        self.status = 'CANCELLED'
        self.save()

    def renew(self):
        if self.can_renew:
            self.status = 'ACTIVE'
            self.save()
            return True
        return False

class PaymentRecord(models.Model):
    """
    Represents a payment record for a subscription.
    Stores payment details and invoice information.
    """
    PAYMENT_STATUS = [
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
        ('REFUNDED', 'Refunded'),
    ]

    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_pdf = models.FileField(upload_to='invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.subscription.user.email}"
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        timestamp = timezone.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"INV-{timestamp}-{random_suffix}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

class TrialUsageStats(models.Model):
    """Track usage statistics for trial subscriptions."""
    subscription = models.OneToOneField(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='usage_stats'
    )
    feature_usage_count = models.JSONField(default=dict)  # Track feature usage counts
    last_active = models.DateTimeField(auto_now=True)
    conversion_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usage stats for {self.subscription.user.email}"

    def track_feature_usage(self, feature_name):
        """Increment usage count for a specific feature."""
        if feature_name not in self.feature_usage_count:
            self.feature_usage_count[feature_name] = 0
        self.feature_usage_count[feature_name] += 1
        self.save()

    def record_conversion(self):
        """Record when a trial is converted to paid subscription."""
        self.conversion_date = timezone.now()
        self.save()
