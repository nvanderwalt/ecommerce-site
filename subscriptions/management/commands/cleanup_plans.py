from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Remove old subscription plans and keep only Basic, Advanced, Premium'

    def handle(self, *args, **options):
        # Keep only the plans with the new names
        plans_to_keep = ['Basic', 'Advanced', 'Premium']
        
        # Get all plans
        all_plans = SubscriptionPlan.objects.all()
        
        for plan in all_plans:
            if plan.name not in plans_to_keep:
                self.stdout.write(f'Deleting old plan: {plan.name}')
                plan.delete()
            else:
                self.stdout.write(f'Keeping plan: {plan.name}')
        
        # Verify we have exactly 3 plans
        remaining_plans = SubscriptionPlan.objects.all()
        self.stdout.write(f'\nRemaining plans:')
        for plan in remaining_plans:
            self.stdout.write(f'- {plan.name} (€{plan.price}/month)')
        
        self.stdout.write(self.style.SUCCESS(f'\nCleanup complete! {remaining_plans.count()} plans remaining.')) 