#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_site.settings')
django.setup()

from subscriptions.models import SubscriptionPlan
from decimal import Decimal

# Create subscription plans
plans = [
    {
        'name': 'Basic Plan',
        'description': 'Perfect for beginners starting their fitness journey',
        'price': Decimal('9.99'),
        'duration_days': 30,
        'features': 'Basic workout plans, Email support, Progress tracking',
        'is_active': True
    },
    {
        'name': 'Premium Plan', 
        'description': 'Advanced features for serious fitness enthusiasts',
        'price': Decimal('19.99'),
        'duration_days': 30,
        'features': 'Premium workout plans, Personal trainer consultation, Advanced analytics, Priority support',
        'is_active': True
    },
    {
        'name': 'Elite Plan',
        'description': 'Ultimate fitness experience with all features',
        'price': Decimal('29.99'),
        'duration_days': 30,
        'features': 'All premium features, 1-on-1 coaching, Custom meal plans, Exclusive content',
        'is_active': True
    }
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )
    if created:
        print(f"Created: {plan.name}")
    else:
        print(f"Already exists: {plan.name}")

print("Subscription plans setup complete!") 