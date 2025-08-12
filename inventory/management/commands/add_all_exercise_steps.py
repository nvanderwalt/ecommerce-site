from django.core.management.base import BaseCommand
from inventory.models import ExercisePlan, ExerciseStep

class Command(BaseCommand):
    help = 'Add exercise steps to all exercise plans'

    def handle(self, *args, **options):
        # Define exercise steps for different difficulty levels
        beginner_steps = [
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
                'name': 'Bodyweight Squats',
                'description': 'Stand with feet shoulder-width apart, toes slightly turned out. Lower your body as if sitting back into a chair, keeping your chest up and knees behind your toes. Go as low as you can while maintaining good form, then push back up through your heels.',
                'duration_minutes': 8,
                'sets': 3,
                'reps': 12,
                'rest_minutes': 2,
            },
            {
                'order': 3,
                'name': 'Wall Push-ups',
                'description': 'Stand facing a wall, arms extended at shoulder height. Place your hands on the wall and lower your body toward the wall, then push back to starting position. Keep your body in a straight line.',
                'duration_minutes': 8,
                'sets': 3,
                'reps': 10,
                'rest_minutes': 2,
            },
            {
                'order': 4,
                'name': 'Plank Hold',
                'description': 'Get into a forearm plank position with elbows under shoulders and body in a straight line from head to heels. Engage your core and hold this position. Focus on breathing steadily.',
                'duration_minutes': 5,
                'sets': 3,
                'reps': 1,
                'rest_minutes': 1,
            },
            {
                'order': 5,
                'name': 'Standing Calf Raises',
                'description': 'Stand with feet shoulder-width apart. Rise up onto your toes, then slowly lower back down. You can hold onto a wall or chair for balance if needed.',
                'duration_minutes': 6,
                'sets': 3,
                'reps': 15,
                'rest_minutes': 1,
            },
            {
                'order': 6,
                'name': 'Cool-down & Stretching',
                'description': 'Finish with 5 minutes of static stretching. Focus on major muscle groups: chest, shoulders, back, hips, quadriceps, hamstrings, and calves. Hold each stretch for 20-30 seconds.',
                'duration_minutes': 8,
                'sets': 1,
                'reps': 1,
                'rest_minutes': 0,
            }
        ]

        intermediate_steps = [
            {
                'order': 1,
                'name': 'Dynamic Warm-up',
                'description': 'Start with 8 minutes of dynamic movements: arm circles, leg swings, hip circles, torso twists, and light jogging in place. Gradually increase intensity.',
                'duration_minutes': 12,
                'sets': 1,
                'reps': 1,
                'rest_minutes': 1,
            },
            {
                'order': 2,
                'name': 'Push-ups',
                'description': 'Start in a plank position with hands slightly wider than shoulders. Lower your body until your chest nearly touches the floor, then push back up. Keep your core tight and body in a straight line.',
                'duration_minutes': 10,
                'sets': 3,
                'reps': 12,
                'rest_minutes': 2,
            },
            {
                'order': 3,
                'name': 'Walking Lunges',
                'description': 'Step forward with one leg and lower your body until both knees are bent at 90-degree angles. Your front knee should be directly above your ankle. Push back to starting position and repeat with the other leg.',
                'duration_minutes': 10,
                'sets': 3,
                'reps': 12,
                'rest_minutes': 2,
            },
            {
                'order': 4,
                'name': 'Mountain Climbers',
                'description': 'Start in a plank position. Quickly alternate bringing your knees toward your chest, as if running in place. Keep your core engaged and maintain a steady pace.',
                'duration_minutes': 8,
                'sets': 3,
                'reps': 20,
                'rest_minutes': 1,
            },
            {
                'order': 5,
                'name': 'Side Plank',
                'description': 'Lie on your side with legs stacked. Prop yourself up on your forearm, keeping your body in a straight line. Hold this position, engaging your core and glutes.',
                'duration_minutes': 8,
                'sets': 3,
                'reps': 1,
                'rest_minutes': 1,
            },
            {
                'order': 6,
                'name': 'Burpees',
                'description': 'Start standing, then squat down and place your hands on the ground. Jump your feet back into a plank position, do a push-up, jump your feet back to your hands, and explosively jump up.',
                'duration_minutes': 10,
                'sets': 3,
                'reps': 8,
                'rest_minutes': 2,
            },
            {
                'order': 7,
                'name': 'Cool-down & Stretching',
                'description': 'Finish with 7 minutes of static stretching. Focus on all major muscle groups and hold each stretch for 30 seconds. Include deep breathing exercises.',
                'duration_minutes': 10,
                'sets': 1,
                'reps': 1,
                'rest_minutes': 0,
            }
        ]

        advanced_steps = [
            {
                'order': 1,
                'name': 'Advanced Warm-up',
                'description': 'Start with 10 minutes of high-intensity dynamic movements: jumping jacks, high knees, butt kicks, arm circles, leg swings, and mobility exercises for all joints.',
                'duration_minutes': 15,
                'sets': 1,
                'reps': 1,
                'rest_minutes': 1,
            },
            {
                'order': 2,
                'name': 'Diamond Push-ups',
                'description': 'Form a diamond shape with your hands under your chest. Lower your body until your chest nearly touches your hands, then push back up. This targets your triceps more intensely.',
                'duration_minutes': 12,
                'sets': 4,
                'reps': 15,
                'rest_minutes': 2,
            },
            {
                'order': 3,
                'name': 'Pistol Squats',
                'description': 'Stand on one leg with the other leg extended in front. Lower your body as far as you can while keeping your balance, then push back up. This is an advanced single-leg exercise.',
                'duration_minutes': 15,
                'sets': 3,
                'reps': 8,
                'rest_minutes': 2,
            },
            {
                'order': 4,
                'name': 'Advanced Burpees',
                'description': 'Perform a burpee with a pull-up at the end. After jumping up, immediately jump to grab a bar and perform a pull-up. This adds upper body strength to the cardio exercise.',
                'duration_minutes': 12,
                'sets': 4,
                'reps': 10,
                'rest_minutes': 2,
            },
            {
                'order': 5,
                'name': 'Plank Variations',
                'description': 'Perform a series of plank variations: standard plank, side plank, reverse plank, and plank with leg lifts. Hold each variation for 30 seconds.',
                'duration_minutes': 10,
                'sets': 3,
                'reps': 1,
                'rest_minutes': 1,
            },
            {
                'order': 6,
                'name': 'Mountain Climbers with Twist',
                'description': 'Perform mountain climbers but twist your knee toward the opposite elbow as you bring it forward. This adds rotation and core engagement.',
                'duration_minutes': 10,
                'sets': 3,
                'reps': 25,
                'rest_minutes': 1,
            },
            {
                'order': 7,
                'name': 'Advanced Cool-down',
                'description': 'Finish with 10 minutes of comprehensive stretching and mobility work. Include dynamic stretches, static holds, and deep breathing exercises.',
                'duration_minutes': 12,
                'sets': 1,
                'reps': 1,
                'rest_minutes': 0,
            }
        ]

        # Get all exercise plans
        plans = ExercisePlan.objects.all()
        
        for plan in plans:
            self.stdout.write(f"Processing plan: {plan.name} (ID: {plan.id})")
            
            # Clear existing steps
            plan.steps.all().delete()
            self.stdout.write(f"  Cleared existing steps for {plan.name}")
            
            # Choose steps based on difficulty
            if plan.difficulty == 'beginner':
                steps_data = beginner_steps
            elif plan.difficulty == 'intermediate':
                steps_data = intermediate_steps
            elif plan.difficulty == 'advanced':
                steps_data = advanced_steps
            else:
                steps_data = beginner_steps  # Default to beginner
            
            # Create the exercise steps
            for step_data in steps_data:
                step = ExerciseStep.objects.create(
                    plan=plan,
                    **step_data
                )
                self.stdout.write(f"  Created step {step.order}: {step.name}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added {len(steps_data)} exercise steps to {plan.name}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed! Added exercise steps to all {plans.count()} exercise plans.'
            )
        ) 