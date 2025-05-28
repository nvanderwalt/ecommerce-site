from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import UserSubscription, SubscriptionPlan

User = get_user_model()

class TestEmail(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test plan with features
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            plan_type='PREMIUM',
            description='Premium features for fitness enthusiasts',
            price=29.99,
            features=[
                'Premium Workouts',
                '1-on-1 personal training sessions'
            ],
            duration_months=1
        )
        
        # Create subscription
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='TRIAL',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=14),
            is_trial=True,
            trial_end_date=timezone.now() + timedelta(days=14)
        )

    def test_trial_reminder_email(self):
        """Test that trial reminder email is sent correctly"""
        from ..utils import send_trial_reminder_email
        
        # Send reminder email
        send_trial_reminder_email(self.user, self.subscription, 3)
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Your Premium Plan Trial Ends in 3 Days', email.subject)
        self.assertIn(self.user.first_name, email.body)
        self.assertIn(self.plan.name, email.body)
        self.assertIn('Convert to Paid Plan', email.body)

    def test_trial_ended_email(self):
        """Test that trial ended email is sent correctly"""
        from ..utils import send_trial_ended_email
        
        # Send trial ended email
        send_trial_ended_email(self.user, self.subscription)
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Your Premium Plan Trial Has Ended', email.subject)
        self.assertIn(self.user.first_name, email.body)
        self.assertIn(self.plan.name, email.body)
        self.assertIn('View Subscription Plans', email.body)

    def test_email_template_variables(self):
        """Test that email templates contain all required variables"""
        from django.template.loader import render_to_string
        from django.conf import settings
        
        # Test trial reminder template
        reminder_context = {
            'user': self.user,
            'subscription': self.subscription,
            'days_remaining': 3,
            'trial_end_date': self.subscription.trial_end_date,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }
        reminder_html = render_to_string(
            'subscriptions/emails/trial_reminder.html',
            reminder_context
        )
        
        # Check for required variables in reminder template
        self.assertIn(self.user.first_name, reminder_html)
        self.assertIn(self.plan.name, reminder_html)
        self.assertIn('3 days', reminder_html)
        
        # Test trial ended template
        ended_context = {
            'user': self.user,
            'subscription': self.subscription,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }
        ended_html = render_to_string(
            'subscriptions/emails/trial_ended.html',
            ended_context
        )
        
        # Check for required variables in ended template
        self.assertIn(self.user.first_name, ended_html)
        self.assertIn(self.plan.name, ended_html)
        self.assertIn('20% off', ended_html) 