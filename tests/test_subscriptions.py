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
        
    def test_subscription_renewal(self):
        """Test subscription renewal handling."""
        # Create test subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() + timedelta(days=1),
            stripe_subscription_id='sub_test123',
            is_auto_renewal=True
        )
        
        # Create test webhook payload for subscription renewal
        payload = {
            'type': 'customer.subscription.updated',
            'data': {
                'object': {
                    'id': 'sub_test123',
                    'status': 'active',
                    'current_period_end': int((timezone.now() + timedelta(days=30)).timestamp())
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
        
        # Verify subscription was renewed
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'ACTIVE')
        self.assertTrue(subscription.end_date > timezone.now())
        
    def test_invalid_webhook_payload(self):
        """Test handling of invalid webhook payloads."""
        # Test with missing signature
        response = self.client.post(
            reverse('subscriptions:webhook'),
            data=json.dumps({'type': 'test.event'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test with invalid JSON
        response = self.client.post(
            reverse('subscriptions:webhook'),
            data='invalid json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        self.assertEqual(response.status_code, 400)
        
    def test_subscription_expiration(self):
        """Test subscription expiration handling."""
        # Create expired subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=1),
            stripe_subscription_id='sub_test123'
        )
        
        # Create test webhook payload for subscription expiration
        payload = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_test123'
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
        
        # Verify subscription was marked as expired
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'EXPIRED')
        
    def test_error_handling(self):
        """Test error handling in subscription operations."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test invalid plan ID
        response = self.client.post(
            reverse('subscriptions:create_checkout', args=[99999]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # Test unauthorized subscription access
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        subscription = UserSubscription.objects.create(
            user=other_user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        response = self.client.post(
            reverse('subscriptions:user_subscription'),
            {
                'subscription_id': subscription.id,
                'action': 'cancel'
            }
        )
        self.assertEqual(response.status_code, 404)
        
    def test_subscription_status_transitions(self):
        """Test various subscription status transitions."""
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Test ACTIVE -> PAYMENT_FAILED
        subscription.status = 'PAYMENT_FAILED'
        subscription.save()
        self.assertEqual(subscription.status, 'PAYMENT_FAILED')
        
        # Test PAYMENT_FAILED -> ACTIVE (after successful payment)
        subscription.status = 'ACTIVE'
        subscription.save()
        self.assertEqual(subscription.status, 'ACTIVE')
        
        # Test ACTIVE -> CANCELLED
        subscription.status = 'CANCELLED'
        subscription.save()
        self.assertEqual(subscription.status, 'CANCELLED')
        
        # Test CANCELLED -> EXPIRED
        subscription.end_date = timezone.now() - timedelta(days=1)
        subscription.save()
        self.assertEqual(subscription.status, 'EXPIRED')
        
    def test_trial_period(self):
        """Test subscription trial period handling."""
        # Create trial subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='TRIAL',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=14),  # 14-day trial
            stripe_subscription_id='sub_test123',
            is_trial=True
        )
        
        # Test trial expiration
        subscription.end_date = timezone.now() - timedelta(days=1)
        subscription.save()
        
        # Verify subscription status
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'EXPIRED')
        
    def test_concurrent_subscriptions(self):
        """Test handling of concurrent subscription attempts."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create active subscription
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Try to create another subscription
        response = self.client.post(
            reverse('subscriptions:create_checkout', args=[self.premium_plan.id]),
            content_type='application/json'
        )
        
        # Should be prevented
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
    def test_plan_change_validation(self):
        """Test validation of plan changes."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create active subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Try to switch to same plan
        response = self.client.post(
            reverse('subscriptions:switch_plan', args=[self.basic_plan.id]),
            content_type='application/json'
        )
        
        # Should be prevented
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # Try to switch to inactive plan
        self.premium_plan.is_active = False
        self.premium_plan.save()
        
        response = self.client.post(
            reverse('subscriptions:switch_plan', args=[self.premium_plan.id]),
            content_type='application/json'
        )
        
        # Should be prevented
        self.assertEqual(response.status_code, 404)
        
    def test_subscription_usage_limits(self):
        """Test subscription usage limits and restrictions."""
        # Create subscription with usage limits
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123',
            usage_count=0,
            max_usage=100
        )
        
        # Test usage tracking
        subscription.usage_count += 1
        subscription.save()
        
        # Verify usage count
        subscription.refresh_from_db()
        self.assertEqual(subscription.usage_count, 1)
        
        # Test usage limit
        subscription.usage_count = 100
        subscription.save()
        
        # Verify subscription is marked as usage limited
        subscription.refresh_from_db()
        self.assertTrue(subscription.is_usage_limited())
        
    def test_subscription_proration(self):
        """Test subscription proration handling during plan changes."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create active subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now() - timedelta(days=15),  # Halfway through billing period
            end_date=timezone.now() + timedelta(days=15),
            stripe_subscription_id='sub_test123'
        )
        
        # Mock Stripe proration calculation
        with patch('stripe.Subscription.modify') as mock_modify:
            mock_modify.return_value = MagicMock(
                id='sub_test123',
                proration_date=int(timezone.now().timestamp()),
                items=MagicMock(data=[MagicMock(price=MagicMock(id='price_test'))])
            )
            
            # Test plan upgrade with proration
            response = self.client.post(
                reverse('subscriptions:switch_plan', args=[self.premium_plan.id]),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertIn('proration_amount', data)
        
    def test_subscription_pause_resume(self):
        """Test subscription pause and resume functionality."""
        # Create active subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Test pausing subscription
        subscription.pause_subscription()
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'PAUSED')
        
        # Test resuming subscription
        subscription.resume_subscription()
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'ACTIVE')
        
        # Test pause during trial
        trial_subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='TRIAL',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=14),
            stripe_subscription_id='sub_test456',
            is_trial=True
        )
        
        # Should not be able to pause trial
        with self.assertRaises(ValueError):
            trial_subscription.pause_subscription()
        
    def test_subscription_refund(self):
        """Test subscription refund handling."""
        # Create subscription with payment
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123',
            payment_id='pi_test123'
        )
        
        # Mock Stripe refund
        with patch('stripe.Refund.create') as mock_refund:
            mock_refund.return_value = MagicMock(id='ref_test123')
            
            # Test partial refund
            refund_amount = 500  # $5.00
            subscription.refund_subscription(refund_amount)
            
            mock_refund.assert_called_once_with(
                payment_intent='pi_test123',
                amount=refund_amount
            )
            
            # Test full refund
            subscription.refund_subscription()
            self.assertEqual(subscription.status, 'REFUNDED')
        
    def test_subscription_grace_period(self):
        """Test subscription grace period handling."""
        # Create subscription with grace period
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            stripe_subscription_id='sub_test123',
            grace_period_days=3
        )
        
        # Test entering grace period
        subscription.end_date = timezone.now() - timedelta(days=1)
        subscription.save()
        
        # Should be in grace period
        self.assertTrue(subscription.is_in_grace_period())
        self.assertEqual(subscription.status, 'GRACE_PERIOD')
        
        # Test grace period expiration
        subscription.end_date = timezone.now() - timedelta(days=4)
        subscription.save()
        
        # Should be expired
        self.assertFalse(subscription.is_in_grace_period())
        self.assertEqual(subscription.status, 'EXPIRED')
        
    def test_subscription_reactivation(self):
        """Test subscription reactivation after expiration."""
        # Create expired subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='EXPIRED',
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30),
            stripe_subscription_id='sub_test123'
        )
        
        # Mock Stripe subscription reactivation
        with patch('stripe.Subscription.modify') as mock_modify:
            mock_modify.return_value = MagicMock(
                id='sub_test123',
                status='active',
                current_period_end=int((timezone.now() + timedelta(days=30)).timestamp())
            )
            
            # Test reactivation
            subscription.reactivate_subscription()
            subscription.refresh_from_db()
            
            self.assertEqual(subscription.status, 'ACTIVE')
            self.assertTrue(subscription.end_date > timezone.now()) 