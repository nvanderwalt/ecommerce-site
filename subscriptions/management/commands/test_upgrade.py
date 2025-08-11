from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from subscriptions.models import UserSubscription, SubscriptionPlan
from datetime import timedelta


class Command(BaseCommand):
    help = 'Test subscription upgrade process'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTING SUBSCRIPTION UPGRADE ===")
        
        # Get a user and plans
        user = User.objects.first()
        basic_plan = SubscriptionPlan.objects.filter(name__icontains='basic').first()
        premium_plan = SubscriptionPlan.objects.filter(name__icontains='premium').first()
        
        if not user or not basic_plan or not premium_plan:
            self.stdout.write("ERROR: Need at least one user and basic/premium plans")
            return
        
        self.stdout.write(f"Testing with user: {user.username}")
        self.stdout.write(f"Basic plan: {basic_plan.name} (${basic_plan.price})")
        self.stdout.write(f"Premium plan: {premium_plan.name} (${premium_plan.price})")
        
        # Create a basic subscription first
        basic_subscription = UserSubscription.objects.create(
            user=user,
            plan=basic_plan,
            status='ACTIVE',
            stripe_subscription_id='test_basic_123',
            end_date=timezone.now() + timedelta(days=30),
            auto_renew=True
        )
        
        self.stdout.write(f"Created basic subscription: {basic_subscription.id}")
        self.stdout.write(f"Basic subscription active: {basic_subscription.is_active}")
        
        # Now simulate an upgrade to premium
        basic_subscription.plan = premium_plan
        basic_subscription.end_date = timezone.now() + timedelta(days=30)
        basic_subscription.save()
        
        self.stdout.write(f"Upgraded to premium subscription: {basic_subscription.id}")
        self.stdout.write(f"Premium subscription active: {basic_subscription.is_active}")
        self.stdout.write(f"Current plan: {basic_subscription.plan.name}")
        
        # Check if profile would see this subscription
        active_subscription = UserSubscription.objects.filter(
            user=user,
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).first()
        
        if active_subscription:
            self.stdout.write(f"Profile would see: {active_subscription.plan.name} subscription")
            self.stdout.write(f"Subscription active: {active_subscription.is_active}")
        else:
            self.stdout.write("ERROR: Profile would NOT see any active subscription")
        
        self.stdout.write("=== TEST COMPLETE ===") 