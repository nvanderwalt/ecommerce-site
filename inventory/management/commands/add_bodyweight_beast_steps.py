from django.core.management.base import BaseCommand
from inventory.models import ExercisePlan, ExerciseStep

class Command(BaseCommand):
    help = 'Add exercise steps to the Bodyweight Beast plan'

    def handle(self, *args, **options):
        try:
            # Get the Bodyweight Beast plan
            plan = ExercisePlan.objects.get(id=6)
            self.stdout.write(f"Found plan: {plan.name}")
            
            # Clear existing steps
            plan.steps.all().delete()
            self.stdout.write("Cleared existing steps")
            
            # Define the exercise steps for Bodyweight Beast
            steps_data = [
                {
                    'order': 1,
                    'name': 'Warm-up & Mobility',
                    'description': 'Start with 5 minutes of light cardio (jumping jacks, high knees, or jogging in place) followed by dynamic stretches for your arms, legs, and core. Focus on shoulder circles, arm swings, hip circles, and gentle torso twists.',
                    'duration_minutes': 10,
                    'sets': 1,
                    'reps': 1,
                    'rest_minutes': 1,
                },
                {
                    'order': 2,
                    'name': 'Push-ups',
                    'description': 'Start in a plank position with hands slightly wider than shoulders. Lower your body until your chest nearly touches the floor, then push back up. Keep your core tight and body in a straight line. If regular push-ups are too challenging, start with knee push-ups.',
                    'duration_minutes': 8,
                    'sets': 3,
                    'reps': 10,
                    'rest_minutes': 2,
                },
                {
                    'order': 3,
                    'name': 'Squats',
                    'description': 'Stand with feet shoulder-width apart, toes slightly turned out. Lower your body as if sitting back into a chair, keeping your chest up and knees behind your toes. Go as low as you can while maintaining good form, then push back up through your heels.',
                    'duration_minutes': 8,
                    'sets': 3,
                    'reps': 15,
                    'rest_minutes': 2,
                },
                {
                    'order': 4,
                    'name': 'Plank Hold',
                    'description': 'Get into a forearm plank position with elbows under shoulders and body in a straight line from head to heels. Engage your core and hold this position. Focus on breathing steadily and maintaining proper form.',
                    'duration_minutes': 5,
                    'sets': 3,
                    'reps': 1,
                    'rest_minutes': 1,
                },
                {
                    'order': 5,
                    'name': 'Lunges',
                    'description': 'Step forward with one leg and lower your body until both knees are bent at 90-degree angles. Your front knee should be directly above your ankle, and your back knee should be close to the ground. Push back to starting position and repeat with the other leg.',
                    'duration_minutes': 8,
                    'sets': 3,
                    'reps': 10,
                    'rest_minutes': 2,
                },
                {
                    'order': 6,
                    'name': 'Mountain Climbers',
                    'description': 'Start in a plank position. Quickly alternate bringing your knees toward your chest, as if running in place. Keep your core engaged and maintain a steady pace. This exercise works your core, shoulders, and cardiovascular system.',
                    'duration_minutes': 6,
                    'sets': 3,
                    'reps': 20,
                    'rest_minutes': 1,
                },
                {
                    'order': 7,
                    'name': 'Burpees',
                    'description': 'Start standing, then squat down and place your hands on the ground. Jump your feet back into a plank position, do a push-up, jump your feet back to your hands, and explosively jump up with arms overhead. This is a full-body exercise that builds strength and endurance.',
                    'duration_minutes': 8,
                    'sets': 3,
                    'reps': 8,
                    'rest_minutes': 2,
                },
                {
                    'order': 8,
                    'name': 'Cool-down & Stretching',
                    'description': 'Finish with 5 minutes of static stretching. Focus on major muscle groups: chest, shoulders, back, hips, quadriceps, hamstrings, and calves. Hold each stretch for 20-30 seconds and breathe deeply.',
                    'duration_minutes': 7,
                    'sets': 1,
                    'reps': 1,
                    'rest_minutes': 0,
                }
            ]
            
            # Create the exercise steps
            for step_data in steps_data:
                step = ExerciseStep.objects.create(
                    plan=plan,
                    **step_data
                )
                self.stdout.write(f"Created step {step.order}: {step.name}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added {len(steps_data)} exercise steps to {plan.name}'
                )
            )
            
        except ExercisePlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Exercise plan with ID 6 not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 