from django.contrib import admin
from .models import Product, UserProfile, Review

admin.site.register(Product)
admin.site.register(UserProfile)
admin.site.register(Review)
