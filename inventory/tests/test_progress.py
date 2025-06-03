from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import ExercisePlan, ExerciseStep, ExercisePlanProgress

User = get_user_model()

class ProgressTrackingTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.plan = ExercisePlan.objects.create(
            name='Test Plan',
            slug='test-plan',
            description='Test Description',
            difficulty='BEG',
            duration_minutes=30,
            calories_burn=200,
            price=29.99
        )
        self.step1 = ExerciseStep.objects.create(
            plan=self.plan,
            order=1,
            name='Step 1',
            description='First step',
            duration_minutes=10,
            sets=3,
            reps=12
        )
        self.step2 = ExerciseStep.objects.create(
            plan=self.plan,
            order=2,
            name='Step 2',
            description='Second step',
            duration_minutes=10,
            sets=3,
            reps=12
        )
        self.step3 = ExerciseStep.objects.create(
            plan=self.plan,
            order=3,
            name='Step 3',
            description='Third step',
            duration_minutes=10,
            sets=3,
            reps=12
        )
        self.progress = ExercisePlanProgress.objects.create(
            user=self.user,
            plan=self.plan,
            current_step=self.step1,
            start_date=timezone.now()
        )
    
    def test_progress_creation(self):
        """Test progress tracking creation."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test progress creation
        response = self.client.post(
            reverse('start_plan', args=[self.plan.slug])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify progress was created
        progress = ExercisePlanProgress.objects.filter(
            user=self.user,
            plan=self.plan
        ).first()
        self.assertIsNotNone(progress)
        self.assertEqual(progress.current_step, self.step1)
    
    def test_step_completion(self):
        """Test step completion."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test completing a step
        response = self.client.post(
            reverse('complete_step', args=[self.plan.slug, self.step1.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify step was completed
        self.progress.refresh_from_db()
        self.assertIn(self.step1, self.progress.completed_steps.all())
        self.assertEqual(self.progress.current_step, self.step2)
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        # Complete first step
        self.progress.complete_step(self.step1)
        self.assertEqual(self.progress.get_progress_percentage(), 33.33)
        
        # Complete second step
        self.progress.complete_step(self.step2)
        self.assertEqual(self.progress.get_progress_percentage(), 66.67)
        
        # Complete third step
        self.progress.complete_step(self.step3)
        self.assertEqual(self.progress.get_progress_percentage(), 100)
    
    def test_plan_completion(self):
        """Test plan completion."""
        # Complete all steps
        self.progress.complete_step(self.step1)
        self.progress.complete_step(self.step2)
        self.progress.complete_step(self.step3)
        
        # Mark plan as completed
        self.progress.is_completed = True
        self.progress.completion_date = timezone.now()
        self.progress.save()
        
        # Verify completion
        self.progress.refresh_from_db()
        self.assertTrue(self.progress.is_completed)
        self.assertIsNotNone(self.progress.completion_date)
        self.assertEqual(self.progress.get_progress_percentage(), 100)
    
    def test_progress_dashboard(self):
        """Test progress dashboard view."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test dashboard view
        response = self.client.get(reverse('progress_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/progress_dashboard.html')
        self.assertContains(response, 'Test Plan')
    
    def test_progress_history(self):
        """Test progress history view."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Complete some steps
        self.progress.complete_step(self.step1)
        self.progress.complete_step(self.step2)
        
        # Test history view
        response = self.client.get(reverse('progress_history', args=[self.plan.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/progress_history.html')
        self.assertContains(response, 'Step 1')
        self.assertContains(response, 'Step 2') 