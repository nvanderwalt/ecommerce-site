from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from subscriptions.models import UserSubscription


class Command(BaseCommand):
    help = 'Check subscription status for debugging'

    def handle(self, *args, **options):
        self.stdout.write("=== SUBSCRIPTION STATUS CHECK ===")
        
        # Get all users
        users = User.objects.all()
        self.stdout.write(f"Total users: {users.count()}")
        
        for user in users:
            self.stdout.write(f"\n--- User: {user.username} (ID: {user.id}) ---")
            
            # Get all subscriptions for this user
            subscriptions = UserSubscription.objects.filter(user=user)
            self.stdout.write(f"Total subscriptions: {subscriptions.count()}")
            
            if subscriptions.exists():
                for sub in subscriptions:
                    self.stdout.write(f"  Subscription {sub.id}:")
                    self.stdout.write(f"    - Status: {sub.status}")
                    self.stdout.write(f"    - Plan: {sub.plan.name if sub.plan else 'None'}")
                    self.stdout.write(f"    - Start date: {sub.start_date}")
                    self.stdout.write(f"    - End date: {sub.end_date}")
                    self.stdout.write(f"    - Current time: {timezone.now()}")
                    self.stdout.write(f"    - Is active: {sub.is_active}")
                    self.stdout.write(f"    - Auto renew: {sub.auto_renew}")
                    self.stdout.write(f"    - Stripe ID: {sub.stripe_subscription_id}")
            else:
                self.stdout.write("  No subscriptions found")
            
            # Check what the profile view would find
            active_subscription = user.usersubscription_set.filter(
                status='ACTIVE',
                end_date__gt=timezone.now()
            ).first()
            
            self.stdout.write(f"  Profile view active subscription: {active_subscription.id if active_subscription else 'None'}")
        
        self.stdout.write("\n=== END CHECK ===") 