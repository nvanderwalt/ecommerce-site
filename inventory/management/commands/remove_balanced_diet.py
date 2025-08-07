from django.core.management.base import BaseCommand
from inventory.models import NutritionPlan


class Command(BaseCommand):
    help = 'Remove the "Balanced Diet" nutrition plan'

    def handle(self, *args, **options):
        # Find all nutrition plans with "Balanced" in the name
        balanced_plans = NutritionPlan.objects.filter(name__icontains='balanced')
        
        if not balanced_plans.exists():
            self.stdout.write("No nutrition plans with 'Balanced' in the name found.")
            return
        
        self.stdout.write(f"Found {balanced_plans.count()} nutrition plan(s) with 'Balanced' in the name:")
        
        for plan in balanced_plans:
            self.stdout.write(f"  - ID: {plan.id}, Name: {plan.name}, Diet Type: {plan.get_diet_type_display()}")
        
        # Remove all balanced diet plans
        count = balanced_plans.count()
        balanced_plans.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully removed {count} nutrition plan(s) with 'Balanced' in the name.")
        ) 