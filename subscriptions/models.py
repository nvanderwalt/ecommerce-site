from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SubscriptionPlan(models.Model):
    """
    Represents a subscription plan that users can subscribe to.
    Each plan has specific features, duration, and pricing.
    """
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
    """
    Represents a user's subscription to a specific plan.
    Tracks the subscription status, duration, and renewal settings.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending'),
        ('SWITCHING', 'Switching'),  # New status for plan switching
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
        """
        Checks if the subscription is currently active based on status and dates.
        Returns True if subscription is active and within valid date range.
        """
        now = timezone.now()
        return (
            self.status == 'ACTIVE' and
            self.start_date <= now and
            self.end_date > now
        )

    def cancel_subscription(self, immediate=False):
        """
        Cancels the subscription with option for immediate or end-of-period cancellation.
        
        Args:
            immediate (bool): If True, cancels immediately. If False, cancels at period end.
            
        Returns:
            bool: True if cancellation was successful
        """
        try:
            if self.stripe_subscription_id:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Subscription.modify(
                    self.stripe_subscription_id,
                    cancel_at_period_end=not immediate
                )
                
                if immediate:
                    stripe.Subscription.delete(self.stripe_subscription_id)
                    self.status = 'CANCELLED'
                    self.end_date = timezone.now()
                else:
                    self.status = 'CANCELLED'
                
                self.is_auto_renewal = False
                self.save()
                return True
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return False

    def switch_plan(self, new_plan):
        """
        Initiates a plan switch to a new subscription plan.
        
        Args:
            new_plan: The SubscriptionPlan instance to switch to
            
        Returns:
            bool: True if the switch was initiated successfully
        """
        if not self.is_active():
            return False
            
        if self.plan == new_plan:
            return False
            
        self.status = 'SWITCHING'
        self.save()
        
        # Create a new subscription record for the switch
        UserSubscription.objects.create(
            user=self.user,
            plan=new_plan,
            status='PENDING',
            start_date=timezone.now(),
            end_date=self.end_date,  # Keep the same end date
            is_auto_renewal=self.is_auto_renewal
        )
        
        return True

    class Meta:
        ordering = ['-created_at']
