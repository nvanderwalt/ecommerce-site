from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['goal', 'fitness_level', 'dietary_preference']
        widgets = {
            'goal': forms.TextInput(attrs={'placeholder': 'Your fitness goal'}),
            'fitness_level': forms.TextInput(attrs={'placeholder': 'Beginner / Intermediate / Advanced'}),
            'dietary_preference': forms.TextInput(attrs={'placeholder': 'Vegan / Keto / etc.'}),
        }
