from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan, UserSubscription

class UserSubscriptionRenewalTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            plan_type='BASIC',
            price=10.00,
            description='Test plan',
            features=['feature1', 'feature2'],
            duration_months=1,
            is_active=True
        )
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            start_date=timezone.now() - timezone.timedelta(days=29),
            end_date=timezone.now() + timezone.timedelta(days=1),
            auto_renew=True
        )

    def test_renew_subscription_extends_end_date(self):
        old_end = self.subscription.end_date
        renewed = self.subscription.renew_subscription()
        self.subscription.refresh_from_db()
        self.assertTrue(renewed)
        self.assertEqual(self.subscription.status, 'ACTIVE')
        self.assertTrue(self.subscription.end_date > old_end)

    def test_renew_subscription_auto_renew_off(self):
        self.subscription.auto_renew = False
        self.subscription.save()
        renewed = self.subscription.renew_subscription()
        self.assertFalse(renewed)

    def test_expired_subscription_status(self):
        self.subscription.end_date = timezone.now() - timezone.timedelta(days=1)
        self.subscription.save()
        self.assertFalse(self.subscription.is_active())
        self.subscription.status = 'EXPIRED'
        self.subscription.save()
        self.assertEqual(self.subscription.status, 'EXPIRED') 