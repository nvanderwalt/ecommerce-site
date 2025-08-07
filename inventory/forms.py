from django import forms
from .models import UserProfile, Review

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['goal', 'fitness_level', 'dietary_preference', 'phone_number', 
                 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
        widgets = {
            'goal': forms.TextInput(attrs={'placeholder': 'Your fitness goal'}),
            'fitness_level': forms.TextInput(attrs={'placeholder': 'Beginner / Intermediate / Advanced'}),
            'dietary_preference': forms.TextInput(attrs={'placeholder': 'Vegan / Keto / etc.'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
            'address_line1': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, etc.'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'}),
        }
