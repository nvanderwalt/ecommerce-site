from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.utils import timezone
import stripe
import json
from unittest.mock import patch, MagicMock

User = get_user_model()

class StripeWebhookTest(TestCase):
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
            description='Test Description',
            price=29.99,
            duration_months=1,
            is_active=True
        )
        
        # Create test client
        self.client = Client()
        
        # Mock Stripe API key and webhook secret
        self.stripe_secret = 'whsec_test_secret'
        self.stripe_signature = 'test_signature'

    @patch('stripe.Webhook.construct_event')
    def test_checkout_session_completed(self, mock_construct_event):
        """Test handling of checkout.session.completed webhook event."""
        # Mock the Stripe event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'mode': 'subscription',
                    'subscription': 'sub_test123',
                    'metadata': {
                        'plan_id': str(self.plan.id),
                        'user_id': str(self.user.id)
                    }
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Mock email sending
        with patch('subscriptions.utils.send_mail') as mock_send_mail:
            # Send webhook request
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data=json.dumps(mock_event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=self.stripe_signature
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Check subscription was created
            subscription = UserSubscription.objects.filter(
                user=self.user,
                plan=self.plan,
                stripe_subscription_id='sub_test123'
            ).first()
            self.assertIsNotNone(subscription)
            self.assertEqual(subscription.status, 'ACTIVE')
            
            # Check email was sent
            mock_send_mail.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    def test_subscription_deleted(self, mock_construct_event):
        """Test handling of customer.subscription.deleted webhook event."""
        # Create active subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            stripe_subscription_id='sub_test123',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Mock the Stripe event
        mock_event = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_test123'
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Mock email sending
        with patch('subscriptions.utils.send_mail') as mock_send_mail:
            # Send webhook request
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data=json.dumps(mock_event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=self.stripe_signature
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Refresh subscription from db
            subscription.refresh_from_db()
            
            # Check subscription was cancelled
            self.assertEqual(subscription.status, 'CANCELLED')
            
            # Check email was sent
            mock_send_mail.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    def test_payment_failed(self, mock_construct_event):
        """Test handling of invoice.payment_failed webhook event."""
        # Create active subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            stripe_subscription_id='sub_test123',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Mock the Stripe event
        mock_event = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'subscription': 'sub_test123'
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Mock email sending
        with patch('subscriptions.utils.send_mail') as mock_send_mail:
            # Send webhook request
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data=json.dumps(mock_event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=self.stripe_signature
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Refresh subscription from db
            subscription.refresh_from_db()
            
            # Check subscription status was updated
            self.assertEqual(subscription.status, 'PAYMENT_FAILED')
            
            # Check email was sent
            mock_send_mail.assert_called_once()

    def test_invalid_signature(self):
        """Test webhook with invalid signature."""
        response = self.client.post(
            reverse('subscriptions:webhook'),
            data='{}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400) 