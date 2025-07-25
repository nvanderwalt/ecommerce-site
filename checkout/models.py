from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(blank=True, null=True)  # For anonymous users

    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.email})"
        return f"Order {self.id} - {user_info} - {self.status}"

    class Meta:
        ordering = ['-created_at']
