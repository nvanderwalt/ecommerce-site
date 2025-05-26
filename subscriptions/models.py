from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import stripe
from django.conf import settings
import logging
import random
import string

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
        ('PENDING_RENEWAL', 'Pending Renewal'),
        ('TRIAL', 'Trial'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def cancel_subscription(self, immediate=False):
        """Cancel the subscription either immediately or at the end of the billing period."""
        try:
            if self.stripe_subscription_id:
                # Cancel the subscription in Stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                if immediate:
                    # Cancel immediately
                    stripe.Subscription.delete(self.stripe_subscription_id)
                    self.status = 'CANCELLED'
                    self.end_date = timezone.now()
                    self.auto_renew = False
                else:
                    # Cancel at period end
                    stripe.Subscription.modify(
                        self.stripe_subscription_id,
                        cancel_at_period_end=True
                    )
                    self.status = 'CANCELLED'
                    self.auto_renew = False
            else:
                # Handle non-Stripe subscriptions
                if immediate:
                    self.status = 'CANCELLED'
                    self.end_date = timezone.now()
                    self.auto_renew = False
                else:
                    self.status = 'CANCELLED'
                    self.auto_renew = False
            
            self.save()
            return True
        except Exception as e:
            print(f"Error cancelling subscription: {str(e)}")
            return False

    def is_active(self):
        """Check if the subscription is currently active."""
        return (
            self.status == 'ACTIVE' and
            self.end_date > timezone.now()
        )

    def get_remaining_days(self):
        """Get the number of days remaining in the subscription."""
        if not self.is_active():
            return 0
        return (self.end_date - timezone.now()).days

    def renew_subscription(self):
        """Renew the subscription for another billing period."""
        try:
            if self.stripe_subscription_id:
                # Handle Stripe subscription renewal
                stripe.api_key = settings.STRIPE_SECRET_KEY
                subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
                
                if subscription.status == 'active':
                    # Update end date based on current period end
                    self.end_date = timezone.datetime.fromtimestamp(
                        subscription.current_period_end,
                        tz=timezone.utc
                    )
                    self.status = 'ACTIVE'
                    self.auto_renew = True
                    self.save()
                    return True
            else:
                # Handle non-Stripe subscription renewal
                if self.auto_renew:
                    # Extend the subscription by the plan's duration
                    self.end_date = self.end_date + timezone.timedelta(
                        days=30 * self.plan.duration_months
                    )
                    self.status = 'ACTIVE'
                    self.save()
                    return True
            
            return False
        except Exception as e:
            print(f"Error renewing subscription: {str(e)}")
            return False

    def switch_plan(self, new_plan):
        """Switch to a new subscription plan."""
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
            stripe_subscription_id=self.stripe_subscription_id,
            auto_renew=self.auto_renew
        )
        
        return True

    def start_trial(self, days=14):
        """Start a trial period for the subscription."""
        if self.is_trial:
            return False
        
        self.is_trial = True
        self.status = 'TRIAL'
        self.trial_end_date = timezone.now() + timezone.timedelta(days=days)
        self.save()
        return True

    def is_trial_active(self):
        """Check if the trial period is still active."""
        return (
            self.is_trial and
            self.trial_end_date and
            self.trial_end_date > timezone.now()
        )

    def get_trial_remaining_days(self):
        """Get the number of days remaining in the trial period."""
        if not self.is_trial_active():
            return 0
        return (self.trial_end_date - timezone.now()).days

    def convert_trial_to_paid(self):
        """Convert a trial subscription to a paid subscription."""
        if not self.is_trial:
            return False
        
        self.is_trial = False
        self.status = 'ACTIVE'
        self.trial_end_date = None
        self.save()
        return True

    class Meta:
        ordering = ['-created_at']

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
