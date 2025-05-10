from django import forms
from .models import UserProfile, Review

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['goal', 'fitness_level', 'dietary_preference']
        widgets = {
            'goal': forms.TextInput(attrs={'placeholder': 'Your fitness goal'}),
            'fitness_level': forms.TextInput(attrs={'placeholder': 'Beginner / Intermediate / Advanced'}),
            'dietary_preference': forms.TextInput(attrs={'placeholder': 'Vegan / Keto / etc.'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'}),
        }
