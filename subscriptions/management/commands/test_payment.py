from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from subscriptions.models import UserSubscription, SubscriptionPlan
from subscriptions.views import subscription_success
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
import stripe
from django.conf import settings


class Command(BaseCommand):
    help = 'Test payment flow and subscription creation'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTING PAYMENT FLOW ===")
        
        # Get a user and plan
        user = User.objects.first()
        plan = SubscriptionPlan.objects.first()
        
        if not user or not plan:
            self.stdout.write("ERROR: Need at least one user and one plan")
            return
        
        self.stdout.write(f"Testing with user: {user.username}")
        self.stdout.write(f"Testing with plan: {plan.name}")
        
        # Check current subscriptions
        current_subs = UserSubscription.objects.filter(user=user)
        self.stdout.write(f"Current subscriptions: {current_subs.count()}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/subscription/success/')
        request.user = user
        
        # Mock Stripe subscription data
        mock_subscription_id = 'sub_test_123456'
        mock_stripe_subscription = type('MockSubscription', (), {
            'current_period_end': int(timezone.now().timestamp()) + (30 * 24 * 60 * 60),  # 30 days from now
            'status': 'active'
        })()
        
        # Mock the Stripe API call
        with self.mock_stripe_subscription(mock_stripe_subscription):
            try:
                # Call the subscription_success view
                response = subscription_success(request)
                self.stdout.write(f"Response status: {response.status_code}")
                
                # Check if subscription was created
                new_subs = UserSubscription.objects.filter(user=user)
                self.stdout.write(f"Subscriptions after test: {new_subs.count()}")
                
                if new_subs.exists():
                    latest_sub = new_subs.latest('created_at')
                    self.stdout.write(f"Latest subscription:")
                    self.stdout.write(f"  - ID: {latest_sub.id}")
                    self.stdout.write(f"  - Status: {latest_sub.status}")
                    self.stdout.write(f"  - Plan: {latest_sub.plan.name}")
                    self.stdout.write(f"  - End date: {latest_sub.end_date}")
                    self.stdout.write(f"  - Is active: {latest_sub.is_active}")
                    self.stdout.write(f"  - Stripe ID: {latest_sub.stripe_subscription_id}")
                else:
                    self.stdout.write("ERROR: No subscription was created!")
                    
            except Exception as e:
                self.stdout.write(f"ERROR: {str(e)}")
        
        self.stdout.write("=== END TEST ===")
    
    def mock_stripe_subscription(self, mock_subscription):
        """Context manager to mock Stripe subscription retrieval"""
        from contextlib import contextmanager
        
        @contextmanager
        def mock_context():
            original_retrieve = stripe.Subscription.retrieve
            
            def mock_retrieve(subscription_id):
                return mock_subscription
            
            stripe.Subscription.retrieve = mock_retrieve
            
            try:
                yield
            finally:
                stripe.Subscription.retrieve = original_retrieve
        
        return mock_context() 