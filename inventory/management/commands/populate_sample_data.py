from django.core.management.base import BaseCommand
from inventory.models import Category, Product, ExercisePlan, NutritionPlan, Review
from posts.models import Post
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populate the database with sample data for demonstration'

    def handle(self, *args, **kwargs):
        # Categories
        cat_strength, _ = Category.objects.get_or_create(name='Strength', slug='strength', description='Strength training')
        cat_cardio, _ = Category.objects.get_or_create(name='Cardio', slug='cardio', description='Cardio equipment')
        cat_nutrition, _ = Category.objects.get_or_create(name='Nutrition', slug='nutrition', description='Nutrition plans')
        cat_accessories, _ = Category.objects.get_or_create(name='Accessories', slug='accessories', description='Accessories for workouts')

        # Products
        products = [
            {'name': 'Dumbbells', 'slug': 'dumbbells', 'desc': 'High-quality dumbbells.', 'price': 49.99, 'cat': cat_strength, 'sku': 'DB-001'},
            {'name': 'Treadmill', 'slug': 'treadmill', 'desc': 'Sturdy treadmill for cardio.', 'price': 599.99, 'cat': cat_cardio, 'sku': 'TM-001'},
            {'name': 'Kettlebell', 'slug': 'kettlebell', 'desc': 'Cast iron kettlebell.', 'price': 39.99, 'cat': cat_strength, 'sku': 'KB-001'},
            {'name': 'Yoga Mat', 'slug': 'yoga-mat', 'desc': 'Non-slip yoga mat.', 'price': 19.99, 'cat': cat_accessories, 'sku': 'YM-001'},
            {'name': 'Resistance Bands', 'slug': 'resistance-bands', 'desc': 'Set of resistance bands.', 'price': 24.99, 'cat': cat_accessories, 'sku': 'RB-001'},
            {'name': 'Stationary Bike', 'slug': 'stationary-bike', 'desc': 'Indoor cycling bike.', 'price': 299.99, 'cat': cat_cardio, 'sku': 'SB-001'},
            {'name': 'Pull-Up Bar', 'slug': 'pull-up-bar', 'desc': 'Doorway pull-up bar.', 'price': 34.99, 'cat': cat_strength, 'sku': 'PB-001'},
            {'name': 'Jump Rope', 'slug': 'jump-rope', 'desc': 'Speed jump rope.', 'price': 14.99, 'cat': cat_accessories, 'sku': 'JR-001'},
            {'name': 'Foam Roller', 'slug': 'foam-roller', 'desc': 'High-density foam roller.', 'price': 22.99, 'cat': cat_accessories, 'sku': 'FR-001'},
            {'name': 'Medicine Ball', 'slug': 'medicine-ball', 'desc': 'Weighted medicine ball.', 'price': 29.99, 'cat': cat_strength, 'sku': 'MB-001'},
        ]
        for p in products:
            Product.objects.get_or_create(
                name=p['name'], slug=p['slug'], description=p['desc'], price=p['price'],
                category=p['cat'], stock=10, sku=p['sku'], is_active=True
            )

        # Exercise Plans
        ExercisePlan.objects.get_or_create(
            name='Beginner Strength Plan', slug='beginner-strength', description='A 4-week plan for beginners.',
            price=29.99, duration_weeks=4, difficulty='beginner', category=cat_strength
        )
        ExercisePlan.objects.get_or_create(
            name='Cardio Blast', slug='cardio-blast', description='Intense cardio program.',
            price=49.99, duration_weeks=6, difficulty='intermediate', category=cat_cardio
        )
        ExercisePlan.objects.get_or_create(
            name='Total Body Burn', slug='total-body-burn', description='Full body workout plan.',
            price=89.99, duration_weeks=8, difficulty='advanced', category=cat_strength
        )

        # Nutrition Plans
        NutritionPlan.objects.get_or_create(
            name='Balanced Diet', slug='balanced-diet', description='A balanced meal plan.',
            diet_type='BAL', calories_per_day=2000, protein_grams=150, carbs_grams=250, fat_grams=70, price=29.99
        )
        NutritionPlan.objects.get_or_create(
            name='Vegan Power', slug='vegan-power', description='Plant-based nutrition plan.',
            diet_type='VEGAN', calories_per_day=1800, protein_grams=120, carbs_grams=220, fat_grams=60, price=34.99
        )
        NutritionPlan.objects.get_or_create(
            name='Keto Kickstart', slug='keto-kickstart', description='Low-carb, high-fat plan.',
            diet_type='KETO', calories_per_day=1700, protein_grams=100, carbs_grams=50, fat_grams=120, price=39.99
        )

        # Create a sample user for reviews/posts
        user, _ = User.objects.get_or_create(username='sampleuser', email='sample@example.com')
        user.set_password('samplepass123')
        user.save()

        # Reviews
        for product in Product.objects.all()[:3]:
            Review.objects.get_or_create(product=product, user=user, rating=5, comment=f"Great {product.name}!")

        # Posts
        Post.objects.get_or_create(content='Welcome to FitFusion! This is your fitness community hub.', author=user)
        Post.objects.get_or_create(content='How to Get Started: Tips for new members.', author=user)

        self.stdout.write(self.style.SUCCESS('Full sample data populated!'))