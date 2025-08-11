from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import ExercisePlan, NutritionPlan, ExercisePlanProgress, NutritionPlanProgress

class Command(BaseCommand):
    help = 'Test progress creation for purchased plans'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='User ID to test with')
        parser.add_argument('--exercise-plan-id', type=int, help='Exercise plan ID to test with')
        parser.add_argument('--nutrition-plan-id', type=int, help='Nutrition plan ID to test with')

    def handle(self, *args, **options):
        user_id = options['user_id']
        exercise_plan_id = options['exercise_plan_id']
        nutrition_plan_id = options['nutrition_plan_id']

        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f"Testing with user: {user.username}")

            if exercise_plan_id:
                exercise_plan = ExercisePlan.objects.get(id=exercise_plan_id)
                self.stdout.write(f"Testing exercise plan: {exercise_plan.name}")
                
                # Create progress record
                progress, created = ExercisePlanProgress.objects.get_or_create(
                    user=user,
                    plan=exercise_plan,
                    defaults={'current_step': exercise_plan.steps.first()}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created exercise plan progress for {exercise_plan.name}"))
                else:
                    self.stdout.write(f"Exercise plan progress already exists for {exercise_plan.name}")

            if nutrition_plan_id:
                nutrition_plan = NutritionPlan.objects.get(id=nutrition_plan_id)
                self.stdout.write(f"Testing nutrition plan: {nutrition_plan.name}")
                
                # Create progress record
                progress, created = NutritionPlanProgress.objects.get_or_create(
                    user=user,
                    plan=nutrition_plan,
                    defaults={'current_meal': nutrition_plan.meals.first()}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created nutrition plan progress for {nutrition_plan.name}"))
                else:
                    self.stdout.write(f"Nutrition plan progress already exists for {nutrition_plan.name}")

            # Show all progress records for the user
            exercise_progress = ExercisePlanProgress.objects.filter(user=user)
            nutrition_progress = NutritionPlanProgress.objects.filter(user=user)
            
            self.stdout.write(f"\nUser has {exercise_progress.count()} exercise plan progress records")
            self.stdout.write(f"User has {nutrition_progress.count()} nutrition plan progress records")
            
            for progress in exercise_progress:
                self.stdout.write(f"  - {progress.plan.name}: {'Completed' if progress.is_completed else 'In Progress'}")
            
            for progress in nutrition_progress:
                self.stdout.write(f"  - {progress.plan.name}: {'Completed' if progress.is_completed else 'In Progress'}")

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {user_id} does not exist"))
        except ExercisePlan.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Exercise plan with ID {exercise_plan_id} does not exist"))
        except NutritionPlan.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Nutrition plan with ID {nutrition_plan_id} does not exist"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}")) 