from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import NutritionPlan, NutritionMeal
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Create sample 7-day nutrition plans with meals for each day'

    def handle(self, *args, **options):
        # Get or create a nutritionist user
        nutritionist, created = User.objects.get_or_create(
            username='nutritionist',
            defaults={
                'email': 'nutritionist@fitfusion.com',
                'first_name': 'Dr.',
                'last_name': 'Nutritionist'
            }
        )
        
        if created:
            nutritionist.set_password('password123')
            nutritionist.save()
            self.stdout.write(f'Created nutritionist user: {nutritionist.username}')
        
        # Create sample nutrition plans
        plans_data = [
            {
                'name': 'Balanced 7-Day Meal Plan',
                'description': 'A well-rounded 7-day meal plan designed for general health and fitness. This plan provides balanced nutrition with a variety of foods to keep you satisfied and energized throughout the week.',
                'diet_type': 'BAL',
                'calories_per_day': 2000,
                'protein_grams': 150,
                'carbs_grams': 200,
                'fat_grams': 70,
                'price': 39.99,
                'meals': [
                    # Monday
                    {'day': 1, 'type': 'BRK', 'name': 'Oatmeal with Berries', 'description': 'Creamy oatmeal topped with fresh berries and a drizzle of honey', 'calories': 350, 'protein': 12, 'carbs': 60, 'fat': 8, 'ingredients': 'Oats, mixed berries, honey, almond milk, chia seeds', 'instructions': 'Cook oats with almond milk, top with berries and honey'},
                    {'day': 1, 'type': 'LUN', 'name': 'Grilled Chicken Salad', 'description': 'Fresh mixed greens with grilled chicken breast and light vinaigrette', 'calories': 450, 'protein': 35, 'carbs': 15, 'fat': 25, 'ingredients': 'Mixed greens, chicken breast, olive oil, balsamic vinegar, cherry tomatoes', 'instructions': 'Grill chicken, assemble salad with dressing'},
                    {'day': 1, 'type': 'DIN', 'name': 'Salmon with Quinoa', 'description': 'Baked salmon fillet served with fluffy quinoa and steamed vegetables', 'calories': 550, 'protein': 40, 'carbs': 45, 'fat': 20, 'ingredients': 'Salmon fillet, quinoa, broccoli, olive oil, lemon, herbs', 'instructions': 'Bake salmon, cook quinoa, steam vegetables'},
                    
                    # Tuesday
                    {'day': 2, 'type': 'BRK', 'name': 'Greek Yogurt Parfait', 'description': 'Greek yogurt layered with granola and fresh fruit', 'calories': 320, 'protein': 20, 'carbs': 45, 'fat': 10, 'ingredients': 'Greek yogurt, granola, strawberries, honey', 'instructions': 'Layer yogurt, granola, and fruit in a glass'},
                    {'day': 2, 'type': 'LUN', 'name': 'Turkey Wrap', 'description': 'Whole grain wrap filled with turkey, avocado, and vegetables', 'calories': 480, 'protein': 30, 'carbs': 35, 'fat': 22, 'ingredients': 'Whole grain wrap, turkey breast, avocado, lettuce, tomato', 'instructions': 'Fill wrap with ingredients and roll tightly'},
                    {'day': 2, 'type': 'DIN', 'name': 'Vegetable Stir Fry', 'description': 'Colorful vegetables stir-fried with tofu and brown rice', 'calories': 520, 'protein': 25, 'carbs': 55, 'fat': 18, 'ingredients': 'Mixed vegetables, tofu, brown rice, soy sauce, ginger, garlic', 'instructions': 'Stir-fry vegetables and tofu, serve with rice'},
                    
                    # Wednesday
                    {'day': 3, 'type': 'BRK', 'name': 'Smoothie Bowl', 'description': 'Thick smoothie bowl topped with nuts, seeds, and fresh fruit', 'calories': 380, 'protein': 15, 'carbs': 50, 'fat': 15, 'ingredients': 'Banana, berries, almond milk, protein powder, granola, nuts', 'instructions': 'Blend smoothie ingredients, top with granola and nuts'},
                    {'day': 3, 'type': 'LUN', 'name': 'Quinoa Buddha Bowl', 'description': 'Quinoa bowl with roasted vegetables and tahini dressing', 'calories': 460, 'protein': 18, 'carbs': 55, 'fat': 20, 'ingredients': 'Quinoa, sweet potato, chickpeas, kale, tahini, lemon', 'instructions': 'Cook quinoa, roast vegetables, assemble bowl'},
                    {'day': 3, 'type': 'DIN', 'name': 'Lean Beef Steak', 'description': 'Grilled lean beef steak with roasted potatoes and green beans', 'calories': 580, 'protein': 45, 'carbs': 40, 'fat': 25, 'ingredients': 'Lean beef steak, potatoes, green beans, olive oil, herbs', 'instructions': 'Grill steak, roast potatoes and beans'},
                    
                    # Thursday
                    {'day': 4, 'type': 'BRK', 'name': 'Egg White Omelette', 'description': 'Fluffy egg white omelette filled with spinach and mushrooms', 'calories': 280, 'protein': 25, 'carbs': 8, 'fat': 15, 'ingredients': 'Egg whites, spinach, mushrooms, olive oil, herbs', 'instructions': 'Whisk egg whites, cook with vegetables'},
                    {'day': 4, 'type': 'LUN', 'name': 'Tuna Salad', 'description': 'Fresh tuna salad with mixed greens and light dressing', 'calories': 420, 'protein': 35, 'carbs': 12, 'fat': 28, 'ingredients': 'Tuna, mixed greens, olive oil, lemon, cucumber, red onion', 'instructions': 'Mix tuna with vegetables and dressing'},
                    {'day': 4, 'type': 'DIN', 'name': 'Chicken Fajitas', 'description': 'Grilled chicken fajitas with whole grain tortillas and vegetables', 'calories': 540, 'protein': 38, 'carbs': 45, 'fat': 22, 'ingredients': 'Chicken breast, whole grain tortillas, bell peppers, onion, spices', 'instructions': 'Grill chicken and vegetables, serve in tortillas'},
                    
                    # Friday
                    {'day': 5, 'type': 'BRK', 'name': 'Protein Pancakes', 'description': 'Fluffy protein pancakes served with fresh berries', 'calories': 360, 'protein': 28, 'carbs': 42, 'fat': 12, 'ingredients': 'Protein powder, oats, egg whites, berries, maple syrup', 'instructions': 'Mix ingredients, cook on griddle, top with berries'},
                    {'day': 5, 'type': 'LUN', 'name': 'Mediterranean Salad', 'description': 'Fresh Mediterranean salad with olives, feta, and olive oil', 'calories': 440, 'protein': 18, 'carbs': 20, 'fat': 35, 'ingredients': 'Mixed greens, olives, feta cheese, cucumber, olive oil', 'instructions': 'Combine ingredients and toss with dressing'},
                    {'day': 5, 'type': 'DIN', 'name': 'Shrimp Pasta', 'description': 'Whole grain pasta with shrimp and light tomato sauce', 'calories': 520, 'protein': 32, 'carbs': 55, 'fat': 18, 'ingredients': 'Whole grain pasta, shrimp, tomato sauce, garlic, herbs', 'instructions': 'Cook pasta, sauté shrimp, combine with sauce'},
                    
                    # Saturday
                    {'day': 6, 'type': 'BRK', 'name': 'Avocado Toast', 'description': 'Whole grain toast topped with mashed avocado and poached egg', 'calories': 340, 'protein': 18, 'carbs': 30, 'fat': 20, 'ingredients': 'Whole grain bread, avocado, egg, sea salt, pepper', 'instructions': 'Toast bread, mash avocado, poach egg'},
                    {'day': 6, 'type': 'LUN', 'name': 'Lentil Soup', 'description': 'Hearty lentil soup with vegetables and herbs', 'calories': 380, 'protein': 22, 'carbs': 45, 'fat': 12, 'ingredients': 'Lentils, vegetables, vegetable broth, herbs, spices', 'instructions': 'Simmer lentils with vegetables and broth'},
                    {'day': 6, 'type': 'DIN', 'name': 'Grilled Fish Tacos', 'description': 'Grilled fish tacos with cabbage slaw and lime crema', 'calories': 480, 'protein': 30, 'carbs': 35, 'fat': 25, 'ingredients': 'White fish, corn tortillas, cabbage, lime, crema', 'instructions': 'Grill fish, prepare slaw, assemble tacos'},
                    
                    # Sunday
                    {'day': 7, 'type': 'BRK', 'name': 'French Toast', 'description': 'Whole grain French toast with cinnamon and maple syrup', 'calories': 380, 'protein': 15, 'carbs': 50, 'fat': 15, 'ingredients': 'Whole grain bread, eggs, milk, cinnamon, maple syrup', 'instructions': 'Dip bread in egg mixture, cook on griddle'},
                    {'day': 7, 'type': 'LUN', 'name': 'Chicken Caesar Salad', 'description': 'Classic Caesar salad with grilled chicken breast', 'calories': 460, 'protein': 35, 'carbs': 15, 'fat': 30, 'ingredients': 'Romaine lettuce, chicken breast, Caesar dressing, croutons', 'instructions': 'Grill chicken, assemble salad with dressing'},
                    {'day': 7, 'type': 'DIN', 'name': 'Beef and Vegetable Skewers', 'description': 'Grilled beef and vegetable skewers with brown rice', 'calories': 540, 'protein': 40, 'carbs': 45, 'fat': 22, 'ingredients': 'Beef cubes, vegetables, brown rice, marinade, herbs', 'instructions': 'Marinate beef, grill skewers, cook rice'},
                ]
            },
            {
                'name': 'Vegetarian 7-Day Meal Plan',
                'description': 'A complete 7-day vegetarian meal plan rich in plant-based proteins and nutrients. Perfect for those looking to reduce meat consumption while maintaining optimal nutrition.',
                'diet_type': 'VEG',
                'calories_per_day': 1800,
                'protein_grams': 120,
                'carbs_grams': 220,
                'fat_grams': 65,
                'price': 34.99,
                'meals': [
                    # Monday
                    {'day': 1, 'type': 'BRK', 'name': 'Chia Pudding', 'description': 'Creamy chia pudding with almond milk and fresh berries', 'calories': 320, 'protein': 12, 'carbs': 45, 'fat': 15, 'ingredients': 'Chia seeds, almond milk, berries, honey, vanilla', 'instructions': 'Mix chia with milk, refrigerate overnight, top with berries'},
                    {'day': 1, 'type': 'LUN', 'name': 'Hummus Wrap', 'description': 'Whole grain wrap with hummus, vegetables, and feta cheese', 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 20, 'ingredients': 'Whole grain wrap, hummus, cucumber, tomato, feta', 'instructions': 'Spread hummus on wrap, add vegetables and cheese'},
                    {'day': 1, 'type': 'DIN', 'name': 'Lentil Curry', 'description': 'Spicy lentil curry served with brown rice and naan bread', 'calories': 480, 'protein': 25, 'carbs': 55, 'fat': 18, 'ingredients': 'Lentils, curry spices, coconut milk, brown rice, naan', 'instructions': 'Cook lentils with spices and coconut milk, serve with rice'},
                    
                    # Tuesday
                    {'day': 2, 'type': 'BRK', 'name': 'Smoothie Bowl', 'description': 'Green smoothie bowl with spinach, banana, and granola', 'calories': 350, 'protein': 15, 'carbs': 50, 'fat': 12, 'ingredients': 'Spinach, banana, almond milk, granola, seeds', 'instructions': 'Blend smoothie ingredients, top with granola'},
                    {'day': 2, 'type': 'LUN', 'name': 'Quinoa Salad', 'description': 'Fresh quinoa salad with chickpeas and Mediterranean vegetables', 'calories': 440, 'protein': 20, 'carbs': 55, 'fat': 18, 'ingredients': 'Quinoa, chickpeas, cucumber, tomato, olive oil', 'instructions': 'Cook quinoa, mix with vegetables and dressing'},
                    {'day': 2, 'type': 'DIN', 'name': 'Vegetable Lasagna', 'description': 'Layered vegetable lasagna with ricotta and marinara sauce', 'calories': 520, 'protein': 28, 'carbs': 45, 'fat': 25, 'ingredients': 'Lasagna noodles, ricotta, vegetables, marinara sauce', 'instructions': 'Layer noodles, ricotta, and vegetables, bake'},
                    
                    # Wednesday
                    {'day': 3, 'type': 'BRK', 'name': 'Oatmeal with Nuts', 'description': 'Steel-cut oatmeal topped with mixed nuts and dried fruits', 'calories': 380, 'protein': 18, 'carbs': 55, 'fat': 15, 'ingredients': 'Steel-cut oats, mixed nuts, dried fruits, honey', 'instructions': 'Cook oats, top with nuts and fruits'},
                    {'day': 3, 'type': 'LUN', 'name': 'Falafel Bowl', 'description': 'Falafel served with tahini sauce and mixed vegetables', 'calories': 460, 'protein': 22, 'carbs': 50, 'fat': 20, 'ingredients': 'Falafel, tahini sauce, vegetables, pita bread', 'instructions': 'Serve falafel with vegetables and tahini sauce'},
                    {'day': 3, 'type': 'DIN', 'name': 'Mushroom Risotto', 'description': 'Creamy mushroom risotto with parmesan cheese', 'calories': 480, 'protein': 20, 'carbs': 55, 'fat': 22, 'ingredients': 'Arborio rice, mushrooms, parmesan, vegetable broth', 'instructions': 'Cook risotto with mushrooms and broth, add parmesan'},
                    
                    # Thursday
                    {'day': 4, 'type': 'BRK', 'name': 'Greek Yogurt Bowl', 'description': 'Greek yogurt with honey, nuts, and fresh fruit', 'calories': 320, 'protein': 25, 'carbs': 35, 'fat': 12, 'ingredients': 'Greek yogurt, honey, mixed nuts, berries', 'instructions': 'Top yogurt with honey, nuts, and fruit'},
                    {'day': 4, 'type': 'LUN', 'name': 'Caprese Salad', 'description': 'Fresh mozzarella, tomato, and basil with balsamic glaze', 'calories': 380, 'protein': 18, 'carbs': 15, 'fat': 28, 'ingredients': 'Mozzarella, tomatoes, basil, balsamic glaze, olive oil', 'instructions': 'Arrange ingredients and drizzle with glaze'},
                    {'day': 4, 'type': 'DIN', 'name': 'Vegetable Stir Fry', 'description': 'Colorful vegetable stir fry with tofu and brown rice', 'calories': 440, 'protein': 22, 'carbs': 50, 'fat': 18, 'ingredients': 'Mixed vegetables, tofu, brown rice, soy sauce', 'instructions': 'Stir-fry vegetables and tofu, serve with rice'},
                    
                    # Friday
                    {'day': 5, 'type': 'BRK', 'name': 'Avocado Toast', 'description': 'Whole grain toast with mashed avocado and microgreens', 'calories': 340, 'protein': 12, 'carbs': 35, 'fat': 20, 'ingredients': 'Whole grain bread, avocado, microgreens, sea salt', 'instructions': 'Toast bread, mash avocado, top with microgreens'},
                    {'day': 5, 'type': 'LUN', 'name': 'Mediterranean Bowl', 'description': 'Mediterranean-inspired bowl with quinoa and roasted vegetables', 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 20, 'ingredients': 'Quinoa, roasted vegetables, olives, feta, olive oil', 'instructions': 'Cook quinoa, roast vegetables, assemble bowl'},
                    {'day': 5, 'type': 'DIN', 'name': 'Black Bean Enchiladas', 'description': 'Black bean enchiladas with corn tortillas and enchilada sauce', 'calories': 480, 'protein': 25, 'carbs': 55, 'fat': 22, 'ingredients': 'Black beans, corn tortillas, enchilada sauce, cheese', 'instructions': 'Fill tortillas with beans, roll, cover with sauce'},
                    
                    # Saturday
                    {'day': 6, 'type': 'BRK', 'name': 'Protein Smoothie', 'description': 'Plant-based protein smoothie with banana and almond butter', 'calories': 360, 'protein': 28, 'carbs': 40, 'fat': 15, 'ingredients': 'Plant protein powder, banana, almond butter, almond milk', 'instructions': 'Blend all ingredients until smooth'},
                    {'day': 6, 'type': 'LUN', 'name': 'Chickpea Salad', 'description': 'Fresh chickpea salad with herbs and lemon dressing', 'calories': 380, 'protein': 20, 'carbs': 35, 'fat': 18, 'ingredients': 'Chickpeas, herbs, lemon, olive oil, vegetables', 'instructions': 'Mix chickpeas with herbs and lemon dressing'},
                    {'day': 6, 'type': 'DIN', 'name': 'Vegetable Paella', 'description': 'Spanish vegetable paella with saffron and mixed vegetables', 'calories': 460, 'protein': 18, 'carbs': 55, 'fat': 20, 'ingredients': 'Paella rice, saffron, mixed vegetables, vegetable broth', 'instructions': 'Cook rice with saffron and vegetables in broth'},
                    
                    # Sunday
                    {'day': 7, 'type': 'BRK', 'name': 'Pancakes with Berries', 'description': 'Whole grain pancakes served with fresh berries and maple syrup', 'calories': 380, 'protein': 15, 'carbs': 50, 'fat': 15, 'ingredients': 'Whole grain flour, eggs, milk, berries, maple syrup', 'instructions': 'Mix batter, cook pancakes, top with berries'},
                    {'day': 7, 'type': 'LUN', 'name': 'Greek Salad', 'description': 'Traditional Greek salad with feta cheese and olive oil', 'calories': 420, 'protein': 18, 'carbs': 20, 'fat': 32, 'ingredients': 'Cucumber, tomatoes, olives, feta, olive oil, oregano', 'instructions': 'Combine ingredients and toss with olive oil'},
                    {'day': 7, 'type': 'DIN', 'name': 'Stuffed Bell Peppers', 'description': 'Bell peppers stuffed with quinoa, vegetables, and cheese', 'calories': 440, 'protein': 22, 'carbs': 45, 'fat': 20, 'ingredients': 'Bell peppers, quinoa, vegetables, cheese, tomato sauce', 'instructions': 'Stuff peppers with quinoa mixture, bake'},
                ]
            }
        ]
        
        for plan_data in plans_data:
            # Create or get the nutrition plan
            plan, created = NutritionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'slug': slugify(plan_data['name']),
                    'description': plan_data['description'],
                    'diet_type': plan_data['diet_type'],
                    'calories_per_day': plan_data['calories_per_day'],
                    'protein_grams': plan_data['protein_grams'],
                    'carbs_grams': plan_data['carbs_grams'],
                    'fat_grams': plan_data['fat_grams'],
                    'price': plan_data['price'],
                    'nutritionist': nutritionist,
                    'duration_days': 7,
                }
            )
            
            if created:
                self.stdout.write(f'Created nutrition plan: {plan.name}')
            else:
                self.stdout.write(f'Nutrition plan already exists: {plan.name}')
            
            # Create meals for the plan
            for meal_data in plan_data['meals']:
                meal, created = NutritionMeal.objects.get_or_create(
                    plan=plan,
                    day_of_week=meal_data['day'],
                    meal_type=meal_data['type'],
                    name=meal_data['name'],
                    defaults={
                        'description': meal_data['description'],
                        'calories': meal_data['calories'],
                        'protein_grams': meal_data['protein'],
                        'carbs_grams': meal_data['carbs'],
                        'fat_grams': meal_data['fat'],
                        'ingredients': meal_data['ingredients'],
                        'instructions': meal_data['instructions'],
                        'order': meal_data['day'] * 10 + {'BRK': 1, 'LUN': 2, 'DIN': 3, 'SNK': 4}[meal_data['type']],
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Created meal: {meal.name} (Day {meal.day_of_week}, {meal.get_meal_type_display()})')
        
        self.stdout.write(self.style.SUCCESS('Successfully created 7-day nutrition plans!')) 