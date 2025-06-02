from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ExercisePlan, ExerciseStep, ExercisePlanProgress
from django.utils import timezone

User = get_user_model()

class ExercisePlanTests(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        
        # Create test exercise plan
        self.plan = ExercisePlan.objects.create(
            name='Test Plan',
            description='Test Description',
            difficulty='BEG',
            duration_minutes=30,
            calories_burn=300,
            equipment_needed='Dumbbells, Mat',
            instructor=self.instructor,
            price=29.99,
            is_active=True
        )
        
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
        
        self.step2 = ExerciseStep.objects.create(
            plan=self.plan,
            order=2,
            name='Main Exercise',
            description='Push-ups',
            duration_minutes=10,
            sets=3,
            reps=10
        )
        
        # Set up test client
        self.client = Client()
    
    def test_exercise_plan_list(self):
        """Test exercise plan list view."""
        # Test unauthenticated access
        response = self.client.get(reverse('inventory:exercise_plan_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_list.html')
        self.assertContains(response, 'Test Plan')
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory:exercise_plan_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_list.html')
    
    def test_exercise_plan_detail(self):
        """Test exercise plan detail view."""
        # Test unauthenticated access
        response = self.client.get(reverse('inventory:exercise_plan_detail', args=[self.plan.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_detail.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, 'Warm-up')
        self.assertContains(response, 'Main Exercise')
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory:exercise_plan_detail', args=[self.plan.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_detail.html')
    
    def test_exercise_plan_progress(self):
        """Test exercise plan progress tracking."""
        # Create progress for user
        progress = ExercisePlanProgress.objects.create(
            user=self.user,
            plan=self.plan,
            current_step=self.step1
        )
        
        # Test completing first step
        progress.complete_step(self.step1)
        self.assertEqual(progress.completed_steps.count(), 1)
        self.assertEqual(progress.get_progress_percentage(), 50)
        
        # Test completing second step
        progress.complete_step(self.step2)
        self.assertEqual(progress.completed_steps.count(), 2)
        self.assertEqual(progress.get_progress_percentage(), 100)
        
        # Test progress completion
        progress.is_completed = True
        progress.completion_date = timezone.now()
        progress.save()
        self.assertTrue(progress.is_completed)
        self.assertIsNotNone(progress.completion_date)
    
    def test_exercise_plan_purchase(self):
        """Test exercise plan purchase flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test purchase view
        response = self.client.get(reverse('inventory:purchase_plan', args=[self.plan.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/purchase_plan.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, '29.99')
    
    def test_exercise_plan_filtering(self):
        """Test exercise plan filtering."""
        # Create additional plans
        ExercisePlan.objects.create(
            name='Advanced Plan',
            description='Advanced Description',
            difficulty='ADV',
            duration_minutes=45,
            calories_burn=500,
            equipment_needed='Full Gym',
            instructor=self.instructor,
            price=49.99,
            is_active=True
        )
        
        # Test filtering by difficulty
        response = self.client.get(reverse('inventory:exercise_plan_list') + '?difficulty=BEG')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan')
        
        # Test filtering by duration
        response = self.client.get(reverse('inventory:exercise_plan_list') + '?max_duration=35')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertNotContains(response, 'Advanced Plan') 