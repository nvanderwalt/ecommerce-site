from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from ..models import AccountSettings

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_registration(self):
        """Test user registration."""
        # Test registration form
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        
        # Test registration submission
        response = self.client.post(reverse('account_signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'email2': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify user was created
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Verify account settings were created
        self.assertTrue(hasattr(user, 'account_settings'))
    
    def test_login(self):
        """Test user login."""
        # Test login form
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        
        # Test login submission
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify user is logged in
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_logout(self):
        """Test user logout."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test logout
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify user is logged out
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Test User')
    
    def test_password_reset(self):
        """Test password reset flow."""
        # Test password reset request
        response = self.client.get(reverse('account_reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_reset.html')
        
        # Submit password reset request
        response = self.client.post(reverse('account_reset_password'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
    
    def test_email_verification(self):
        """Test email verification."""
        # Create unverified user
        user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Test email verification
        response = self.client.get(reverse('account_confirm_email', args=['test-token']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/email_confirm.html')
    
    def test_account_settings(self):
        """Test account settings."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test settings page
        response = self.client.get(reverse('accounts:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/settings.html')
        
        # Test updating settings
        response = self.client.post(reverse('accounts:settings'), {
            'email_notifications': True,
            'marketing_emails': False,
            'login_notifications': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify settings were updated
        settings = AccountSettings.objects.get(user=self.user)
        self.assertTrue(settings.email_notifications)
        self.assertFalse(settings.marketing_emails)
        self.assertTrue(settings.login_notifications) 