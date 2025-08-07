from django.core.management.base import BaseCommand
from inventory.models import NutritionPlan


class Command(BaseCommand):
    help = 'Remove duplicate nutrition plans'

    def handle(self, *args, **options):
        # Get all nutrition plans
        plans = NutritionPlan.objects.all()
        
        # Group by name to find duplicates
        plan_groups = {}
        for plan in plans:
            if plan.name not in plan_groups:
                plan_groups[plan.name] = []
            plan_groups[plan.name].append(plan)
        
        # Find and remove duplicates
        removed_count = 0
        for name, plan_list in plan_groups.items():
            if len(plan_list) > 1:
                self.stdout.write(f"Found {len(plan_list)} plans with name: {name}")
                
                # Keep the first one (most recent due to ordering), remove the rest
                for i, plan in enumerate(plan_list[1:], 1):
                    self.stdout.write(f"  Removing duplicate {i}: {plan} (ID: {plan.id})")
                    plan.delete()
                    removed_count += 1
        
        if removed_count == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate nutrition plans found."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully removed {removed_count} duplicate nutrition plan(s).")
            ) 