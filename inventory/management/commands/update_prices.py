from django.core.management.base import BaseCommand
from inventory.models import ExercisePlan

class Command(BaseCommand):
    help = 'Update exercise plan prices to realistic values'

    def handle(self, *args, **kwargs):
        # Update beginner plans
        beginner_plans = ExercisePlan.objects.filter(difficulty='beginner')
        for plan in beginner_plans:
            plan.price = 29.99
            plan.save()
            self.stdout.write(f'Updated {plan.name} price to $29.99')

        # Update intermediate plans
        intermediate_plans = ExercisePlan.objects.filter(difficulty='intermediate')
        for plan in intermediate_plans:
            plan.price = 49.99
            plan.save()
            self.stdout.write(f'Updated {plan.name} price to $49.99')

        # Update advanced plans
        advanced_plans = ExercisePlan.objects.filter(difficulty='advanced')
        for plan in advanced_plans:
            plan.price = 89.99
            plan.save()
            self.stdout.write(f'Updated {plan.name} price to $89.99')

        self.stdout.write(self.style.SUCCESS('All exercise plan prices updated!')) 