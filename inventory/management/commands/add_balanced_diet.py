from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import NutritionPlan
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add a new Balanced Diet nutrition plan'

    def handle(self, *args, **options):
        # Get or create a nutritionist user
        nutritionist, created = User.objects.get_or_create(
            username='nutritionist',
            defaults={
                'email': 'nutritionist@fitfusion.com',
                'first_name': 'Expert',
                'last_name': 'Nutritionist'
            }
        )
        
        # Create the Balanced Diet plan
        balanced_plan = NutritionPlan.objects.create(
            name='Balanced Diet Plan',
            slug='balanced-diet-plan',
            description='A comprehensive nutrition plan designed to provide balanced macronutrients for optimal health and fitness. This plan includes a variety of whole foods to support your fitness goals while maintaining a healthy lifestyle.',
            diet_type='BAL',
            calories_per_day=2000,
            protein_grams=150,
            carbs_grams=200,
            fat_grams=67,
            price=29.99,
            nutritionist=nutritionist,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Balanced Diet Plan:\n'
                f'  - Name: {balanced_plan.name}\n'
                f'  - Calories: {balanced_plan.calories_per_day}/day\n'
                f'  - Protein: {balanced_plan.protein_grams}g\n'
                f'  - Carbs: {balanced_plan.carbs_grams}g\n'
                f'  - Fat: {balanced_plan.fat_grams}g\n'
                f'  - Price: ${balanced_plan.price}'
            )
        ) 