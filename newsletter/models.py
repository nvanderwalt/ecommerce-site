from django.db import models
from django.core.validators import EmailValidator

class Newsletter(models.Model):
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Enter your email address to subscribe to our newsletter"
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
    
    def __str__(self):
        return f"{self.email} - {self.subscribed_at.strftime('%Y-%m-%d')}"
