from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventory.models import NutritionPlan, NutritionMeal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a 7-day keto nutrition plan'

    def handle(self, *args, **options):
        # Get or create a nutritionist user
        nutritionist, created = User.objects.get_or_create(
            username='nutritionist',
            defaults={
                'email': 'nutritionist@fitfusion.com',
                'first_name': 'Dr.',
                'last_name': 'Nutritionist',
                'is_staff': True,
            }
        )
        
        if created:
            nutritionist.set_password('nutritionist123')
            nutritionist.save()
            self.stdout.write(self.style.SUCCESS('Created nutritionist user'))
        
        # Create Keto 7-Day Meal Plan
        keto_plan, created = NutritionPlan.objects.get_or_create(
            name="Keto 7-Day Meal Plan",
            defaults={
                'nutritionist': nutritionist,
                'description': 'A comprehensive 7-day ketogenic meal plan designed to help you achieve and maintain ketosis while enjoying delicious, satisfying meals.',
                'diet_type': 'KET',
                'calories_per_day': 1800,
                'protein_grams': 120,
                'carbs_grams': 25,
                'fat_grams': 140,
                'price': 29.99,
                'sale_price': 24.99,
                'duration_days': 7,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Keto 7-Day Meal Plan'))
        else:
            self.stdout.write(self.style.WARNING('Keto plan already exists'))
            return
        
        # Define meals for each day
        meals_data = [
            # Day 1 - Monday
            {
                'day_of_week': 1,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Avocado & Eggs',
                'description': 'Creamy avocado with perfectly poached eggs',
                'calories': 450,
                'protein_grams': 25,
                'carbs_grams': 8,
                'fat_grams': 35,
                'ingredients': '2 large eggs, 1/2 avocado, 1 tbsp butter, salt, pepper, red pepper flakes',
                'instructions': 'Poach eggs in simmering water. Mash avocado with butter, salt, and pepper. Serve eggs over avocado.',
                'prep_time_minutes': 5,
                'cooking_time_minutes': 8,
            },
            {
                'day_of_week': 1,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Chicken Caesar Salad',
                'description': 'Classic Caesar salad with grilled chicken and keto-friendly dressing',
                'calories': 380,
                'protein_grams': 35,
                'carbs_grams': 6,
                'fat_grams': 22,
                'ingredients': '4 oz grilled chicken breast, 2 cups romaine lettuce, 2 tbsp Caesar dressing, 1/4 cup parmesan cheese, croutons (optional)',
                'instructions': 'Grill chicken until cooked through. Toss lettuce with dressing and parmesan. Top with sliced chicken.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 12,
            },
            {
                'day_of_week': 1,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Salmon with Asparagus',
                'description': 'Pan-seared salmon with roasted asparagus',
                'calories': 520,
                'protein_grams': 40,
                'carbs_grams': 8,
                'fat_grams': 35,
                'ingredients': '6 oz salmon fillet, 1 cup asparagus, 2 tbsp olive oil, lemon, garlic, salt, pepper',
                'instructions': 'Season salmon and sear 4-5 minutes per side. Roast asparagus with olive oil, garlic, salt, and pepper for 15 minutes.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 20,
            },
            
            # Day 2 - Tuesday
            {
                'day_of_week': 2,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Smoothie Bowl',
                'description': 'Creamy smoothie bowl with keto-friendly toppings',
                'calories': 420,
                'protein_grams': 20,
                'carbs_grams': 12,
                'fat_grams': 32,
                'ingredients': '1/2 cup coconut milk, 1/4 cup berries, 1 scoop protein powder, 2 tbsp almond butter, 1 tbsp chia seeds',
                'instructions': 'Blend coconut milk, berries, and protein powder. Top with almond butter and chia seeds.',
                'prep_time_minutes': 5,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 2,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Tuna Salad Lettuce Wraps',
                'description': 'Fresh tuna salad wrapped in crisp lettuce leaves',
                'calories': 350,
                'protein_grams': 30,
                'carbs_grams': 4,
                'fat_grams': 20,
                'ingredients': '1 can tuna, 2 tbsp mayo, 1/4 cup celery, 1/4 cup red onion, 4 large lettuce leaves, salt, pepper',
                'instructions': 'Mix tuna with mayo, celery, onion, salt, and pepper. Spoon into lettuce leaves and roll up.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 2,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Beef Stir-Fry',
                'description': 'Sliced beef with low-carb vegetables in savory sauce',
                'calories': 480,
                'protein_grams': 35,
                'carbs_grams': 10,
                'fat_grams': 28,
                'ingredients': '6 oz beef strips, 1 cup broccoli, 1/2 cup bell peppers, 2 tbsp soy sauce, 1 tbsp sesame oil, garlic, ginger',
                'instructions': 'Stir-fry beef until browned. Add vegetables and stir-fry until tender. Add sauce and seasonings.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 15,
            },
            
            # Day 3 - Wednesday
            {
                'day_of_week': 3,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Chia Pudding',
                'description': 'Creamy chia pudding with coconut and berries',
                'calories': 380,
                'protein_grams': 15,
                'carbs_grams': 14,
                'fat_grams': 28,
                'ingredients': '1/4 cup chia seeds, 1 cup coconut milk, 1/4 cup berries, 1 tbsp sweetener, vanilla extract',
                'instructions': 'Mix chia seeds with coconut milk and sweetener. Refrigerate overnight. Top with berries before serving.',
                'prep_time_minutes': 5,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 3,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Cobb Salad',
                'description': 'Classic Cobb salad with bacon, eggs, and avocado',
                'calories': 420,
                'protein_grams': 25,
                'carbs_grams': 6,
                'fat_grams': 32,
                'ingredients': '2 cups mixed greens, 2 slices bacon, 1 hard-boiled egg, 1/4 avocado, 2 oz chicken, blue cheese, ranch dressing',
                'instructions': 'Arrange greens on plate. Top with crumbled bacon, sliced egg, avocado, chicken, and blue cheese. Drizzle with dressing.',
                'prep_time_minutes': 12,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 3,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Pork Chops with Cauliflower',
                'description': 'Juicy pork chops with roasted cauliflower',
                'calories': 510,
                'protein_grams': 38,
                'carbs_grams': 8,
                'fat_grams': 35,
                'ingredients': '6 oz pork chops, 2 cups cauliflower florets, 2 tbsp olive oil, garlic, rosemary, salt, pepper',
                'instructions': 'Season pork chops and grill 4-5 minutes per side. Roast cauliflower with olive oil, garlic, and rosemary for 25 minutes.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 25,
            },
            
            # Day 4 - Thursday
            {
                'day_of_week': 4,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Breakfast Burrito',
                'description': 'Scrambled eggs with cheese wrapped in low-carb tortilla',
                'calories': 440,
                'protein_grams': 28,
                'carbs_grams': 8,
                'fat_grams': 32,
                'ingredients': '3 eggs, 1/4 cup shredded cheese, 1 low-carb tortilla, 2 tbsp salsa, 1 tbsp sour cream',
                'instructions': 'Scramble eggs with cheese. Warm tortilla and fill with eggs. Top with salsa and sour cream.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 5,
            },
            {
                'day_of_week': 4,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Greek Salad',
                'description': 'Fresh Greek salad with feta and olives',
                'calories': 360,
                'protein_grams': 18,
                'carbs_grams': 8,
                'fat_grams': 28,
                'ingredients': '2 cups mixed greens, 1/4 cup feta cheese, 1/4 cup olives, 1/4 cucumber, 1/4 red onion, olive oil, lemon juice',
                'instructions': 'Combine all ingredients in a bowl. Dress with olive oil and lemon juice. Season with salt and pepper.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 4,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Shrimp Scampi',
                'description': 'Garlic butter shrimp with zucchini noodles',
                'calories': 470,
                'protein_grams': 32,
                'carbs_grams': 6,
                'fat_grams': 35,
                'ingredients': '8 oz shrimp, 2 medium zucchinis, 3 tbsp butter, 3 cloves garlic, lemon, parsley, salt, pepper',
                'instructions': 'Spiralize zucchini into noodles. Sauté shrimp in butter and garlic. Add zucchini noodles and cook until tender.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 12,
            },
            
            # Day 5 - Friday
            {
                'day_of_week': 5,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Breakfast Bowl',
                'description': 'Scrambled eggs with bacon and avocado',
                'calories': 460,
                'protein_grams': 22,
                'carbs_grams': 6,
                'fat_grams': 38,
                'ingredients': '3 eggs, 2 slices bacon, 1/2 avocado, 1/4 cup shredded cheese, salt, pepper',
                'instructions': 'Cook bacon until crispy. Scramble eggs with cheese. Serve with sliced avocado and crumbled bacon.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 10,
            },
            {
                'day_of_week': 5,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Turkey Roll-Ups',
                'description': 'Turkey and cheese rolled in lettuce',
                'calories': 320,
                'protein_grams': 28,
                'carbs_grams': 4,
                'fat_grams': 20,
                'ingredients': '4 oz turkey slices, 2 slices cheese, 4 large lettuce leaves, 1 tbsp mustard, 1/4 cup cucumber',
                'instructions': 'Layer turkey and cheese on lettuce leaves. Add mustard and cucumber. Roll up tightly.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 0,
            },
            {
                'day_of_week': 5,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Chicken Alfredo',
                'description': 'Creamy Alfredo sauce with chicken and zucchini noodles',
                'calories': 520,
                'protein_grams': 35,
                'carbs_grams': 8,
                'fat_grams': 38,
                'ingredients': '6 oz chicken breast, 2 medium zucchinis, 1/2 cup heavy cream, 1/4 cup parmesan, garlic, butter',
                'instructions': 'Cook chicken until done. Spiralize zucchini. Make Alfredo sauce with cream, parmesan, and garlic. Combine all ingredients.',
                'prep_time_minutes': 12,
                'cooking_time_minutes': 15,
            },
            
            # Day 6 - Saturday
            {
                'day_of_week': 6,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Pancakes',
                'description': 'Fluffy almond flour pancakes with berries',
                'calories': 420,
                'protein_grams': 18,
                'carbs_grams': 12,
                'fat_grams': 32,
                'ingredients': '1/2 cup almond flour, 2 eggs, 1/4 cup coconut milk, 1 tbsp sweetener, 1/4 cup berries, butter',
                'instructions': 'Mix almond flour, eggs, coconut milk, and sweetener. Cook on griddle until golden. Serve with berries and butter.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 10,
            },
            {
                'day_of_week': 6,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto BLT Salad',
                'description': 'Bacon, lettuce, and tomato in a fresh salad',
                'calories': 380,
                'protein_grams': 20,
                'carbs_grams': 6,
                'fat_grams': 28,
                'ingredients': '2 cups mixed greens, 3 slices bacon, 1/2 cup cherry tomatoes, 1/4 cup blue cheese, ranch dressing',
                'instructions': 'Cook bacon until crispy. Toss greens with tomatoes, crumbled bacon, and blue cheese. Dress with ranch.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 8,
            },
            {
                'day_of_week': 6,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Steak with Mushrooms',
                'description': 'Grilled steak with sautéed mushrooms',
                'calories': 540,
                'protein_grams': 42,
                'carbs_grams': 6,
                'fat_grams': 38,
                'ingredients': '8 oz steak, 1 cup mushrooms, 2 tbsp butter, garlic, thyme, salt, pepper',
                'instructions': 'Season steak and grill to desired doneness. Sauté mushrooms in butter with garlic and thyme.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 15,
            },
            
            # Day 7 - Sunday
            {
                'day_of_week': 7,
                'meal_type': 'BRK',
                'order': 1,
                'name': 'Keto Frittata',
                'description': 'Baked egg frittata with spinach and cheese',
                'calories': 440,
                'protein_grams': 26,
                'carbs_grams': 6,
                'fat_grams': 34,
                'ingredients': '6 eggs, 1 cup spinach, 1/4 cup shredded cheese, 1/4 cup mushrooms, 2 tbsp heavy cream, salt, pepper',
                'instructions': 'Whisk eggs with cream. Add spinach, cheese, and mushrooms. Bake in oven at 350°F for 20-25 minutes.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 25,
            },
            {
                'day_of_week': 7,
                'meal_type': 'LUN',
                'order': 2,
                'name': 'Keto Taco Salad',
                'description': 'Mexican-inspired salad with ground beef',
                'calories': 420,
                'protein_grams': 32,
                'carbs_grams': 8,
                'fat_grams': 28,
                'ingredients': '4 oz ground beef, 2 cups mixed greens, 1/4 cup shredded cheese, 1/4 cup salsa, 2 tbsp sour cream, taco seasoning',
                'instructions': 'Cook ground beef with taco seasoning. Layer greens, beef, cheese, salsa, and sour cream in a bowl.',
                'prep_time_minutes': 8,
                'cooking_time_minutes': 10,
            },
            {
                'day_of_week': 7,
                'meal_type': 'DIN',
                'order': 3,
                'name': 'Keto Fish Tacos',
                'description': 'Grilled fish in lettuce wraps with avocado',
                'calories': 480,
                'protein_grams': 35,
                'carbs_grams': 8,
                'fat_grams': 32,
                'ingredients': '6 oz white fish, 4 large lettuce leaves, 1/2 avocado, 1/4 cup cabbage slaw, lime, cilantro, salt, pepper',
                'instructions': 'Season fish and grill until flaky. Serve in lettuce wraps with avocado, slaw, lime, and cilantro.',
                'prep_time_minutes': 10,
                'cooking_time_minutes': 12,
            },
        ]
        
        # Create meals
        for meal_data in meals_data:
            meal = NutritionMeal.objects.create(
                plan=keto_plan,
                **meal_data
            )
            self.stdout.write(f'Created meal: {meal.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created Keto 7-Day Meal Plan with {len(meals_data)} meals')) 