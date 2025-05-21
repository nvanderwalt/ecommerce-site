from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json
import stripe
from unittest.mock import patch, MagicMock
from ..models import SubscriptionPlan, UserSubscription

User = get_user_model()

class SubscriptionIntegrationTests(TestCase):
    """Integration tests for subscription functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test plans
        self.basic_plan = SubscriptionPlan.objects.create(
            name='Basic Plan',
            description='Basic subscription plan',
            price=9.99,
            duration_months=1,
            is_active=True
        )
        
        self.premium_plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            description='Premium subscription plan',
            price=19.99,
            duration_months=1,
            is_active=True
        )
        
        # Set up test client
        self.client = Client()
        
        # Mock Stripe API key
        self.stripe_patcher = patch('stripe.api_key', 'test_key')
        self.stripe_patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.stripe_patcher.stop()
        
    def test_subscription_plan_list(self):
        """Test subscription plan list view."""
        # Test unauthenticated access
        response = self.client.get(reverse('subscriptions:plan_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/plan_list.html')
        self.assertContains(response, 'Basic Plan')
        self.assertContains(response, 'Premium Plan')
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('subscriptions:plan_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/plan_list.html')
        
    @patch('stripe.checkout.Session.create')
    def test_create_subscription(self, mock_create):
        """Test subscription creation flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # Mock Stripe checkout session creation
        mock_create.return_value = MagicMock(id='test_session_id')
        
        # Test subscription creation
        response = self.client.post(
            reverse('subscriptions:create_checkout', args=[self.basic_plan.id]),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], 'test_session_id')
        
    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_created(self, mock_construct):
        """Test webhook handling for subscription creation."""
        # Create test webhook payload
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'mode': 'subscription',
                    'subscription': 'sub_test123',
                    'metadata': {
                        'plan_id': str(self.basic_plan.id),
                        'user_id': str(self.user.id)
                    }
                }
            }
        }
        
        # Mock webhook signature verification
        mock_construct.return_value = payload
        
        # Send webhook request
        response = self.client.post(
            reverse('subscriptions:webhook'),
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription was created
        subscription = UserSubscription.objects.filter(
            user=self.user,
            plan=self.basic_plan,
            stripe_subscription_id='sub_test123'
        ).first()
        
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.status, 'ACTIVE')
        
    def test_subscription_cancellation(self):
        """Test subscription cancellation."""
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Test immediate cancellation
        response = self.client.post(
            reverse('subscriptions:user_subscription'),
            {
                'subscription_id': subscription.id,
                'action': 'cancel',
                'immediate': 'true'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify subscription was cancelled
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'CANCELLED')
        
    @patch('stripe.checkout.Session.create')
    def test_plan_switching(self, mock_create):
        """Test subscription plan switching."""
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Mock Stripe checkout session creation
        mock_create.return_value = MagicMock(id='test_session_id')
        
        # Test plan switch initiation
        response = self.client.post(
            reverse('subscriptions:switch_plan', args=[self.premium_plan.id]),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], 'test_session_id')
        
        # Verify subscription status was updated
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'SWITCHING')
        
    def test_payment_failure_handling(self):
        """Test payment failure handling."""
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Create test webhook payload for payment failure
        payload = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'subscription': 'sub_test123'
                }
            }
        }
        
        # Send webhook request
        response = self.client.post(
            reverse('subscriptions:webhook'),
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription status was updated
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'PAYMENT_FAILED') 