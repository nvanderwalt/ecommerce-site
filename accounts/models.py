from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import pyotp

class AccountSettings(models.Model):
    """User account settings and preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_settings')
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    login_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.email}"

    def generate_2fa_secret(self):
        """Generate a new 2FA secret key."""
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def verify_2fa_token(self, token):
        """Verify a 2FA token."""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token)

    def get_2fa_uri(self):
        """Get the 2FA URI for QR code generation."""
        if not self.two_factor_secret:
            self.generate_2fa_secret()
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name="FitFusion"
        )

class SecurityLog(models.Model):
    """Log of security-related events for a user."""
    EVENT_TYPES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('EMAIL_CHANGE', 'Email Change'),
        ('2FA_ENABLE', '2FA Enabled'),
        ('2FA_DISABLE', '2FA Disabled'),
        ('LOGIN_FAILED', 'Failed Login Attempt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} for {self.user.email} at {self.created_at}"

@receiver(post_save, sender=User)
def create_account_settings(sender, instance, created, **kwargs):
    """Create account settings when a new user is created."""
    if created:
        AccountSettings.objects.create(user=instance)
