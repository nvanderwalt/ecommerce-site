from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import NutritionPlan, NutritionMeal, NutritionPlanProgress
from django.utils import timezone
import logging
from unittest.mock import patch

logger = logging.getLogger(__name__)

User = get_user_model()

@override_settings(
    STRIPE_PUBLIC_KEY='pk_test_test',
    STRIPE_SECRET_KEY='sk_test_test'
)
class NutritionPlanTests(TestCase):
    def setUp(self):
        """Set up test data."""
        logger.info("Setting up test data...")
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        logger.info("Created test user")
        
        # Create test nutritionist
        self.nutritionist = User.objects.create_user(
            username='nutritionist',
            email='nutritionist@example.com',
            password='testpass123'
        )
        logger.info("Created test nutritionist")
        
        # Create test nutrition plan
        self.plan = NutritionPlan.objects.create(
            name='Test Plan',
            slug='test-plan',
            description='Test Description',
            diet_type='VEG',
            calories_per_day=2000,
            protein_grams=150,
            carbs_grams=200,
            fat_grams=70,
            nutritionist=self.nutritionist,
            price=29.99,
            is_active=True
        )
        logger.info("Created test nutrition plan")
        
        # Create test meals
        self.meal1 = NutritionMeal.objects.create(
            plan=self.plan,
            order=1,
            name='Breakfast Bowl',
            description='Healthy breakfast bowl',
            meal_type='BRK',
            calories=500,
            protein_grams=30,
            carbs_grams=50,
            fat_grams=20,
            ingredients='Oats, berries, nuts, milk',
            instructions='Mix ingredients and enjoy',
            prep_time_minutes=5,
            cooking_time_minutes=10
        )
        logger.info("Created meal 1")
        
        self.meal2 = NutritionMeal.objects.create(
            plan=self.plan,
            order=2,
            name='Lunch Salad',
            description='Protein-rich salad',
            meal_type='LUN',
            calories=600,
            protein_grams=40,
            carbs_grams=30,
            fat_grams=25,
            ingredients='Chicken, greens, avocado, dressing',
            instructions='Combine ingredients and toss',
            prep_time_minutes=10,
            cooking_time_minutes=15
        )
        logger.info("Created meal 2")
        
        # Set up test client
        self.client = Client()
        # Log in the test user by default
        self.client.login(username='testuser', password='testpass123')
        logger.info("Set up test client and logged in user")
    
    def test_nutrition_plan_list(self):
        """Test nutrition plan list view."""
        logger.info("Testing nutrition plan list view...")
        # Test authenticated access
        response = self.client.get(reverse('inventory:nutrition_plan_list'))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/nutrition_plans.html')
        self.assertContains(response, 'Test Plan')
        
        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(reverse('inventory:nutrition_plan_list'))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_nutrition_plan_detail(self):
        """Test nutrition plan detail view."""
        logger.info("Testing nutrition plan detail view...")
        # Test authenticated access
        response = self.client.get(reverse('inventory:nutrition_plan_detail', args=[self.plan.id]))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/nutrition_plan_detail.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, 'Breakfast Bowl')
        self.assertContains(response, 'Lunch Salad')
        
        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(reverse('inventory:nutrition_plan_detail', args=[self.plan.id]))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_nutrition_plan_progress(self):
        """Test nutrition plan progress tracking."""
        logger.info("Testing nutrition plan progress...")
        # Create progress for user
        progress = NutritionPlanProgress.objects.create(
            user=self.user,
            plan=self.plan,
            current_meal=self.meal1
        )
        logger.info("Created progress object")
        
        # Test completing first meal
        progress.complete_meal(self.meal1)
        self.assertEqual(progress.completed_meals.count(), 1)
        self.assertEqual(progress.get_progress_percentage(), 50)
        logger.info("Completed first meal")
        
        # Test completing second meal
        progress.complete_meal(self.meal2)
        self.assertEqual(progress.completed_meals.count(), 2)
        self.assertEqual(progress.get_progress_percentage(), 100)
        logger.info("Completed second meal")
        
        # Test progress completion
        progress.is_completed = True
        progress.completion_date = timezone.now()
        progress.save()
        self.assertTrue(progress.is_completed)
        self.assertIsNotNone(progress.completion_date)
        logger.info("Marked progress as completed")
    
    @patch('stripe.checkout.Session.create')
    def test_nutrition_plan_purchase(self, mock_create):
        """Test nutrition plan purchase flow."""
        logger.info("Testing nutrition plan purchase...")
        
        # Mock the Stripe API response
        mock_create.return_value = type('obj', (object,), {'id': 'test_session_id'})
        
        # Test purchase view with POST request
        response = self.client.post(
            reverse('inventory:create_plan_checkout_session', args=[self.plan.id])
        )
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 'test_session_id'})
        
        # Test unauthenticated access
        self.client.logout()
        response = self.client.post(
            reverse('inventory:create_plan_checkout_session', args=[self.plan.id])
        )
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_nutrition_plan_filtering(self):
        """Test nutrition plan filtering."""
        logger.info("Testing nutrition plan filtering...")
        # Create additional plan
        NutritionPlan.objects.create(
            name='Advanced Plan',
            slug='advanced-plan',
            description='Advanced Description',
            diet_type='KETO',
            calories_per_day=2500,
            protein_grams=200,
            carbs_grams=50,
            fat_grams=150,
            nutritionist=self.nutritionist,
            price=49.99,
            is_active=True
        )
        logger.info("Created additional plan")
        
        # Test filtering by diet type
        response = self.client.get(reverse('inventory:nutrition_plan_list') + '?diet_type=VEG')
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan')
        
        # Test filtering by calories
        response = self.client.get(reverse('inventory:nutrition_plan_list') + '?max_calories=2200')
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan') 