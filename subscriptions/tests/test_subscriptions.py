from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.core.mail import mail
from unittest.mock import patch, MagicMock
import json

class SubscriptionIntegrationTests(TestCase):
    """Integration tests for subscription functionality."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test plans
        self.basic_plan = SubscriptionPlan.objects.create(
            name='Basic Plan',
            plan_type='BASIC',
            description='Basic features',
            price=9.99,
            features=['Feature 1', 'Feature 2'],
            duration_months=1,
            is_active=True
        )
        
        self.premium_plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            plan_type='PREMIUM',
            description='Premium features',
            price=19.99,
            features=['Feature 1', 'Feature 2', 'Feature 3'],
            duration_months=1,
            is_active=True
        )

    def test_start_trial(self):
        """Test starting a trial subscription."""
        # Start trial
        response = self.client.post(
            reverse('subscriptions:start_trial', args=[self.basic_plan.id])
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify subscription was created
        subscription = UserSubscription.objects.get(user=self.user)
        self.assertTrue(subscription.is_trial)
        self.assertEqual(subscription.status, 'TRIAL')
        self.assertTrue(subscription.is_trial_active())
        self.assertEqual(subscription.get_trial_remaining_days(), 14)

    def test_start_trial_with_active_subscription(self):
        """Test starting a trial when user has active subscription."""
        # Create active subscription
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Try to start trial
        response = self.client.post(
            reverse('subscriptions:start_trial', args=[self.premium_plan.id])
        )
        
        # Check redirect and message
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already have an active subscription' in str(m) for m in messages))

    def test_start_trial_with_previous_trial(self):
        """Test starting a trial when user has used trial before."""
        # Create expired trial subscription
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='EXPIRED',
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() - timedelta(days=16),
            is_trial=True,
            trial_end_date=timezone.now() - timedelta(days=16)
        )
        
        # Try to start new trial
        response = self.client.post(
            reverse('subscriptions:start_trial', args=[self.premium_plan.id])
        )
        
        # Check redirect and message
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already used your trial period' in str(m) for m in messages))

    def test_convert_trial(self):
        """Test converting trial to paid subscription."""
        # Create trial subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='TRIAL',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=14),
            is_trial=True,
            trial_end_date=timezone.now() + timedelta(days=14)
        )
        
        # Mock Stripe checkout session
        with patch('stripe.checkout.Session.create') as mock_create:
            mock_create.return_value = MagicMock(id='test_session_id')
            
            # Convert trial
            response = self.client.post(
                reverse('subscriptions:convert_trial', args=[subscription.id])
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data['id'], 'test_session_id')

    def test_convert_expired_trial(self):
        """Test converting expired trial."""
        # Create expired trial subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='TRIAL',
            start_date=timezone.now() - timedelta(days=15),
            end_date=timezone.now() - timedelta(days=1),
            is_trial=True,
            trial_end_date=timezone.now() - timedelta(days=1)
        )
        
        # Try to convert expired trial
        response = self.client.post(
            reverse('subscriptions:convert_trial', args=[subscription.id])
        )
        
        # Check redirect and message
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('trial period has expired' in str(m) for m in messages))

    def test_trial_reminder_emails(self):
        """Test trial reminder email scheduling."""
        # Create trial subscription
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='TRIAL',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=14),
            is_trial=True,
            trial_end_date=timezone.now() + timedelta(days=14)
        )
        
        # Check reminder emails
        from ..utils import check_trial_notifications
        check_trial_notifications()
        
        # Verify no emails sent (not at reminder days yet)
        self.assertEqual(len(mail.outbox), 0)
        
        # Set trial end to 3 days from now
        subscription.trial_end_date = timezone.now() + timedelta(days=3)
        subscription.save()
        
        # Check reminder emails again
        check_trial_notifications()
        
        # Verify reminder email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Trial Ends in 3 Days', mail.outbox[0].subject) 