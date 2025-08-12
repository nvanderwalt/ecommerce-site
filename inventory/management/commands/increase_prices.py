from django.core.management.base import BaseCommand
from inventory.models import ExercisePlan, NutritionPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Multiply exercise plan and nutrition plan prices by 5'

    def handle(self, *args, **options):
        # Update Exercise Plan prices
        exercise_plans = ExercisePlan.objects.all()
        self.stdout.write("Updating Exercise Plan prices...")
        
        for plan in exercise_plans:
            old_price = plan.price
            new_price = old_price * Decimal('5')  # Multiply by 5
            plan.price = new_price
            plan.save()
            
            self.stdout.write(
                f"  {plan.name}: ${old_price} → ${new_price}"
            )
        
        self.stdout.write(f"Updated {exercise_plans.count()} exercise plans")
        
        # Update Nutrition Plan prices
        nutrition_plans = NutritionPlan.objects.all()
        self.stdout.write("\nUpdating Nutrition Plan prices...")
        
        for plan in nutrition_plans:
            old_price = plan.price
            new_price = old_price * Decimal('5')  # Multiply by 5
            plan.price = new_price
            
            # Also update sale_price if it exists
            if plan.sale_price:
                old_sale_price = plan.sale_price
                new_sale_price = old_sale_price * Decimal('5')
                plan.sale_price = new_sale_price
                self.stdout.write(
                    f"  {plan.name}: ${old_price} → ${new_price} (sale: ${old_sale_price} → ${new_sale_price})"
                )
            else:
                self.stdout.write(
                    f"  {plan.name}: ${old_price} → ${new_price}"
                )
            
            plan.save()
        
        self.stdout.write(f"Updated {nutrition_plans.count()} nutrition plans")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully multiplied prices by 5 for all {exercise_plans.count() + nutrition_plans.count()} plans!'
            )
        ) 