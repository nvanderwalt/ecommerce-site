from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ExercisePlan, ExerciseStep, ExercisePlanProgress
from django.utils import timezone
import logging
from unittest.mock import patch

logger = logging.getLogger(__name__)

User = get_user_model()

@override_settings(
    STRIPE_PUBLIC_KEY='pk_test_test',
    STRIPE_SECRET_KEY='sk_test_test'
)
class ExercisePlanTests(TestCase):
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
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        logger.info("Created test instructor")
        
        # Create test exercise plan
        self.plan = ExercisePlan.objects.create(
            name='Test Plan',
            slug='test-plan',
            description='Test Description',
            difficulty='BEG',
            duration_minutes=30,
            calories_burn=300,
            equipment_needed='Dumbbells, Mat',
            instructor=self.instructor,
            price=29.99,
            is_active=True
        )
        logger.info("Created test exercise plan")
        
        # Create test exercise steps
        self.step1 = ExerciseStep.objects.create(
            plan=self.plan,
            order=1,
            name='Warm-up',
            description='5 minutes of light cardio',
            duration_minutes=5,
            sets=1,
            reps=1
        )
        logger.info("Created step 1")
        
        self.step2 = ExerciseStep.objects.create(
            plan=self.plan,
            order=2,
            name='Main Exercise',
            description='Push-ups',
            duration_minutes=10,
            sets=3,
            reps=10
        )
        logger.info("Created step 2")
        
        # Set up test client
        self.client = Client()
        # Log in the test user by default
        self.client.login(username='testuser', password='testpass123')
        logger.info("Set up test client and logged in user")
    
    def test_exercise_plan_list(self):
        """Test exercise plan list view."""
        logger.info("Testing exercise plan list view...")
        # Test authenticated access
        response = self.client.get(reverse('inventory:exercise_plan_list'))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plans.html')
        self.assertContains(response, 'Test Plan')
        
        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(reverse('inventory:exercise_plan_list'))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_exercise_plan_detail(self):
        """Test exercise plan detail view."""
        logger.info("Testing exercise plan detail view...")
        # Test authenticated access
        response = self.client.get(reverse('inventory:exercise_plan_detail', args=[self.plan.id]))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_detail.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, 'Warm-up')
        self.assertContains(response, 'Main Exercise')
        
        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(reverse('inventory:exercise_plan_detail', args=[self.plan.id]))
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_exercise_plan_progress(self):
        """Test exercise plan progress tracking."""
        logger.info("Testing exercise plan progress...")
        # Create progress for user
        progress = ExercisePlanProgress.objects.create(
            user=self.user,
            plan=self.plan,
            current_step=self.step1
        )
        logger.info("Created progress object")
        
        # Test completing first step
        progress.complete_step(self.step1)
        self.assertEqual(progress.completed_steps.count(), 1)
        self.assertEqual(progress.get_progress_percentage(), 50)
        logger.info("Completed first step")
        
        # Test completing second step
        progress.complete_step(self.step2)
        self.assertEqual(progress.completed_steps.count(), 2)
        self.assertEqual(progress.get_progress_percentage(), 100)
        logger.info("Completed second step")
        
        # Test progress completion
        progress.is_completed = True
        progress.completion_date = timezone.now()
        progress.save()
        self.assertTrue(progress.is_completed)
        self.assertIsNotNone(progress.completion_date)
        logger.info("Marked progress as completed")
    
    @patch('stripe.checkout.Session.create')
    def test_exercise_plan_purchase(self, mock_create):
        """Test exercise plan purchase flow."""
        logger.info("Testing exercise plan purchase...")
        
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
    
    def test_exercise_plan_filtering(self):
        """Test exercise plan filtering."""
        logger.info("Testing exercise plan filtering...")
        # Create additional plans
        ExercisePlan.objects.create(
            name='Advanced Plan',
            slug='advanced-plan',
            description='Advanced Description',
            difficulty='ADV',
            duration_minutes=45,
            calories_burn=500,
            equipment_needed='Full Gym',
            instructor=self.instructor,
            price=49.99,
            is_active=True
        )
        logger.info("Created additional plan")
        
        # Test filtering by difficulty
        response = self.client.get(reverse('inventory:exercise_plan_list') + '?difficulty=BEG')
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan')
        
        # Test filtering by duration
        response = self.client.get(reverse('inventory:exercise_plan_list') + '?max_duration=35')
        logger.info(f"Got response with status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan') 