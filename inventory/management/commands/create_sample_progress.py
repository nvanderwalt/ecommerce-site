from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import ExercisePlan, ExerciseStep, ExercisePlanProgress, NutritionPlan, NutritionMeal, NutritionPlanProgress
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample progress data for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing user: {user.username}'))

        # Get or create an exercise plan
        exercise_plan, created = ExercisePlan.objects.get_or_create(
            name='Beginner Workout Plan',
            defaults={
                'slug': 'beginner-workout-plan',
                'description': 'A perfect plan for beginners',
                'price': 29.99,
                'difficulty': 'beginner',
                'duration_weeks': 4,
                'daily_exercise_minutes': 30
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created exercise plan: {exercise_plan.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing exercise plan: {exercise_plan.name}'))

        # Create exercise steps if they don't exist
        steps_data = [
            {'name': 'Warm-up', 'description': '5 minutes of light cardio', 'duration_minutes': 5, 'sets': 1, 'reps': 1},
            {'name': 'Push-ups', 'description': 'Basic push-ups', 'duration_minutes': 10, 'sets': 3, 'reps': 10},
            {'name': 'Squats', 'description': 'Body weight squats', 'duration_minutes': 10, 'sets': 3, 'reps': 15},
            {'name': 'Cool-down', 'description': '5 minutes of stretching', 'duration_minutes': 5, 'sets': 1, 'reps': 1},
        ]
        
        for i, step_data in enumerate(steps_data, 1):
            step, created = ExerciseStep.objects.get_or_create(
                plan=exercise_plan,
                order=i,
                defaults={
                    'name': step_data['name'],
                    'description': step_data['description'],
                    'duration_minutes': step_data['duration_minutes'],
                    'sets': step_data['sets'],
                    'reps': step_data['reps'],
                    'rest_minutes': 1
                }
            )
            if created:
                self.stdout.write(f'Created exercise step: {step.name}')

        # Get or create a nutrition plan
        nutrition_plan, created = NutritionPlan.objects.get_or_create(
            name='Balanced Nutrition Plan',
            defaults={
                'slug': 'balanced-nutrition-plan',
                'description': 'A balanced nutrition plan for healthy eating',
                'diet_type': 'BAL',
                'calories_per_day': 2000,
                'protein_grams': 150,
                'carbs_grams': 200,
                'fat_grams': 70,
                'price': 39.99
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created nutrition plan: {nutrition_plan.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing nutrition plan: {nutrition_plan.name}'))

        # Create nutrition meals if they don't exist
        meals_data = [
            {'name': 'Healthy Breakfast', 'description': 'Oatmeal with fruits', 'meal_type': 'BRK', 'calories': 400, 'protein_grams': 15, 'carbs_grams': 60, 'fat_grams': 10},
            {'name': 'Protein Lunch', 'description': 'Grilled chicken salad', 'meal_type': 'LUN', 'calories': 500, 'protein_grams': 35, 'carbs_grams': 30, 'fat_grams': 25},
            {'name': 'Balanced Dinner', 'description': 'Salmon with vegetables', 'meal_type': 'DIN', 'calories': 600, 'protein_grams': 40, 'carbs_grams': 45, 'fat_grams': 25},
            {'name': 'Healthy Snack', 'description': 'Greek yogurt with nuts', 'meal_type': 'SNK', 'calories': 200, 'protein_grams': 15, 'carbs_grams': 15, 'fat_grams': 10},
        ]
        
        for i, meal_data in enumerate(meals_data, 1):
            meal, created = NutritionMeal.objects.get_or_create(
                plan=nutrition_plan,
                order=i,
                defaults={
                    'name': meal_data['name'],
                    'description': meal_data['description'],
                    'meal_type': meal_data['meal_type'],
                    'calories': meal_data['calories'],
                    'protein_grams': meal_data['protein_grams'],
                    'carbs_grams': meal_data['carbs_grams'],
                    'fat_grams': meal_data['fat_grams'],
                    'ingredients': 'Fresh ingredients',
                    'instructions': 'Follow healthy cooking methods',
                    'prep_time_minutes': 15,
                    'cooking_time_minutes': 20
                }
            )
            if created:
                self.stdout.write(f'Created nutrition meal: {meal.name}')

        # Create exercise progress
        exercise_progress, created = ExercisePlanProgress.objects.get_or_create(
            user=user,
            plan=exercise_plan,
            defaults={
                'current_step': exercise_plan.steps.first(),
                'start_date': timezone.now() - timedelta(days=7)
            }
        )
        
        if created:
            # Mark first two steps as completed
            steps = list(exercise_plan.steps.all())[:2]
            for step in steps:
                exercise_progress.complete_step(step)
            self.stdout.write(self.style.SUCCESS(f'Created exercise progress with {exercise_progress.completed_steps.count()} completed steps'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing exercise progress'))

        # Create nutrition progress
        nutrition_progress, created = NutritionPlanProgress.objects.get_or_create(
            user=user,
            plan=nutrition_plan,
            defaults={
                'current_meal': nutrition_plan.meals.first(),
                'start_date': timezone.now() - timedelta(days=5)
            }
        )
        
        if created:
            # Mark first meal as completed
            first_meal = nutrition_plan.meals.first()
            if first_meal:
                nutrition_progress.complete_meal(first_meal)
            self.stdout.write(self.style.SUCCESS(f'Created nutrition progress with {nutrition_progress.completed_meals.count()} completed meals'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing nutrition progress'))

        self.stdout.write(self.style.SUCCESS('Sample progress data created successfully!'))
        self.stdout.write(f'Test user: {user.username} (password: testpass123)')
        self.stdout.write('You can now log in and view the progress dashboard.') 