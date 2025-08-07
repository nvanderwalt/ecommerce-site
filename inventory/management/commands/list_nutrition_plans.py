from django.core.management.base import BaseCommand
from inventory.models import NutritionPlan


class Command(BaseCommand):
    help = 'List all nutrition plans'

    def handle(self, *args, **options):
        plans = NutritionPlan.objects.all()
        
        self.stdout.write(f"Found {plans.count()} nutrition plans:")
        self.stdout.write("-" * 50)
        
        for plan in plans:
            self.stdout.write(f"ID: {plan.id}")
            self.stdout.write(f"Name: {plan.name}")
            self.stdout.write(f"Diet Type: {plan.get_diet_type_display()}")
            self.stdout.write(f"Active: {plan.is_active}")
            self.stdout.write(f"Created: {plan.created_at}")
            self.stdout.write("-" * 30) 