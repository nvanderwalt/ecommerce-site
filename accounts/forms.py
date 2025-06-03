from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import AccountSettings

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

class AccountSettingsForm(forms.ModelForm):
    """Form for updating account settings."""
    class Meta:
        model = AccountSettings
        fields = ['email_notifications', 'marketing_emails', 'login_notifications']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'login_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'}) 