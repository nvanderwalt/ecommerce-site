from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import SubscriptionPlan, UserSubscription

User = get_user_model()

class SubscriptionTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test plan
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            plan_type='BASIC',
            price=9.99,
            description='Test subscription plan',
            duration_months=1,
            features=['Feature 1', 'Feature 2'],
            is_active=True
        )
        
        # Create client
        self.client = Client()
        
    def test_plan_list_view(self):
        """Test that plan list view works correctly"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Get plan list page
        response = self.client.get(reverse('subscription_plans'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/plan_list.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, '9.99')
        
    def test_dashboard_view(self):
        """Test that dashboard view works correctly"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Get dashboard page
        response = self.client.get(reverse('subscription_dashboard'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/dashboard.html')
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, 'Active')
        
    def test_subscription_cancel(self):
        """Test subscription cancellation"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Cancel subscription
        response = self.client.post(reverse('subscription_cancel'))
        
        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Refresh subscription from database
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'CANCELLED')
        
    def test_subscription_renew(self):
        """Test subscription renewal"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='CANCELLED',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Renew subscription
        response = self.client.post(reverse('subscription_renew'))
        
        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Refresh subscription from database
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'ACTIVE') 