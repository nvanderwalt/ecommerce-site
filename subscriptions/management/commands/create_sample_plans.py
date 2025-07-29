from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample subscription plans'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Basic Plan',
                'plan_type': 'BASIC',
                'description': 'Perfect for beginners starting their fitness journey',
                'price': Decimal('9.99'),
                'duration_months': 1,
                'features': ['Basic workout plans', 'Email support', 'Progress tracking'],
                'is_active': True
            },
            {
                'name': 'Premium Plan',
                'plan_type': 'PREMIUM',
                'description': 'Advanced features for serious fitness enthusiasts',
                'price': Decimal('19.99'),
                'duration_months': 1,
                'features': ['Premium workout plans', 'Personal trainer consultation', 'Advanced analytics', 'Priority support'],
                'is_active': True
            },
            {
                'name': 'Elite Plan',
                'plan_type': 'PRO',
                'description': 'Ultimate fitness experience with all features',
                'price': Decimal('29.99'),
                'duration_months': 1,
                'features': ['All premium features', '1-on-1 coaching', 'Custom meal plans', 'Exclusive content'],
                'is_active': True
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Subscription plans setup complete!')
        ) 