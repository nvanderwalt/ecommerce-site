from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from subscriptions.models import UserSubscription, SubscriptionPlan
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create a test subscription to verify UI'

    def handle(self, *args, **options):
        self.stdout.write("=== CREATING TEST SUBSCRIPTION ===")
        
        # Get a user and plan
        user = User.objects.first()
        plan = SubscriptionPlan.objects.first()
        
        if not user or not plan:
            self.stdout.write("ERROR: Need at least one user and one plan")
            return
        
        self.stdout.write(f"Creating subscription for user: {user.username}")
        self.stdout.write(f"Using plan: {plan.name}")
        
        # Check current subscriptions
        current_subs = UserSubscription.objects.filter(user=user)
        self.stdout.write(f"Current subscriptions: {current_subs.count()}")
        
        # Create a test subscription
        end_date = timezone.now() + timedelta(days=30)
        
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            status='ACTIVE',
            stripe_subscription_id='test_sub_123',
            end_date=end_date,
            auto_renew=True
        )
        
        self.stdout.write(f"Created subscription ID: {subscription.id}")
        self.stdout.write(f"Status: {subscription.status}")
        self.stdout.write(f"End date: {subscription.end_date}")
        self.stdout.write(f"Is active: {subscription.is_active}")
        
        # Check what the profile view would find
        active_subscription = user.usersubscription_set.filter(
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).first()
        
        self.stdout.write(f"Profile view active subscription: {active_subscription.id if active_subscription else 'None'}")
        
        self.stdout.write("=== TEST SUBSCRIPTION CREATED ===")
        self.stdout.write("Now go to your profile page and check if it shows as active!") 