from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update subscription plan names to Basic, Advanced, Premium'

    def handle(self, *args, **options):
        # Update Basic Plan
        basic_plan = SubscriptionPlan.objects.filter(plan_type='BASIC').first()
        if basic_plan:
            basic_plan.name = 'Basic'
            basic_plan.description = 'Perfect for beginners starting their fitness journey'
            basic_plan.price = Decimal('9.99')
            basic_plan.features = ['Basic workout plans', 'Email support', 'Progress tracking']
            basic_plan.save()
            self.stdout.write(self.style.SUCCESS(f'Updated: {basic_plan.name}'))
        
        # Update Premium Plan to Advanced
        premium_plan = SubscriptionPlan.objects.filter(plan_type='PREMIUM').first()
        if premium_plan:
            premium_plan.name = 'Advanced'
            premium_plan.description = 'Advanced features for serious fitness enthusiasts'
            premium_plan.price = Decimal('19.99')
            premium_plan.features = ['Advanced workout plans', 'Personal trainer consultation', 'Advanced analytics', 'Priority support']
            premium_plan.save()
            self.stdout.write(self.style.SUCCESS(f'Updated: {premium_plan.name}'))
        
        # Update Elite Plan to Premium
        pro_plan = SubscriptionPlan.objects.filter(plan_type='PRO').first()
        if pro_plan:
            pro_plan.name = 'Premium'
            pro_plan.description = 'Ultimate fitness experience with all features'
            pro_plan.price = Decimal('29.99')
            pro_plan.features = ['All premium features', '1-on-1 coaching', 'Custom meal plans', 'Exclusive content']
            pro_plan.save()
            self.stdout.write(self.style.SUCCESS(f'Updated: {pro_plan.name}'))

        self.stdout.write(self.style.SUCCESS('Subscription plan names updated successfully!')) 