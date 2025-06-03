from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from .forms import UserProfileForm, AccountSettingsForm, CustomPasswordChangeForm
from .models import SecurityLog, AccountSettings
import qrcode
import io
import base64

# Create your views here.

@login_required
def account_settings(request):
    """View for managing account settings."""
    if request.method == 'POST':
        settings_form = AccountSettingsForm(request.POST, instance=request.user.account_settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Account settings updated successfully.')
            return redirect('accounts:settings')
    else:
        settings_form = AccountSettingsForm(instance=request.user.account_settings)

    # Get recent security logs
    security_logs = SecurityLog.objects.filter(user=request.user)[:10]

    context = {
        'settings_form': settings_form,
        'security_logs': security_logs,
    }
    return render(request, 'accounts/settings.html', context)

@login_required
def profile_edit(request):
    """View for editing user profile information."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def change_password(request):
    """View for changing user password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Log password change
            SecurityLog.objects.create(
                user=request.user,
                event_type='PASSWORD_CHANGE',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:settings')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def security_logs(request):
    """View for displaying security logs."""
    logs = SecurityLog.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/security_logs.html', {'logs': logs})

@login_required
def setup_2fa(request):
    """View for setting up two-factor authentication."""
    settings = request.user.account_settings
    
    if request.method == 'POST':
        token = request.POST.get('token')
        if settings.verify_2fa_token(token):
            settings.two_factor_enabled = True
            settings.save()
            
            # Log 2FA enablement
            SecurityLog.objects.create(
                user=request.user,
                event_type='2FA_ENABLE',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Two-factor authentication has been enabled.')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(settings.get_2fa_uri())
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'accounts/setup_2fa.html', {
        'qr_code': qr_code,
        'secret': settings.two_factor_secret
    })

@login_required
def disable_2fa(request):
    """View for disabling two-factor authentication."""
    if request.method == 'POST':
        settings = request.user.account_settings
        token = request.POST.get('token')
        
        if settings.verify_2fa_token(token):
            settings.two_factor_enabled = False
            settings.two_factor_secret = ''
            settings.save()
            
            # Log 2FA disablement
            SecurityLog.objects.create(
                user=request.user,
                event_type='2FA_DISABLE',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Two-factor authentication has been disabled.')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
    
    return render(request, 'accounts/disable_2fa.html')

@login_required
def verify_email(request):
    """View for verifying email address."""
    settings = request.user.account_settings
    
    if request.method == 'POST':
        token = request.POST.get('token')
        if token == settings.email_verification_token:
            settings.email_verified = True
            settings.email_verification_token = ''
            settings.save()
            
            # Log email verification
            SecurityLog.objects.create(
                user=request.user,
                event_type='EMAIL_VERIFY',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Email address verified successfully.')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Invalid verification token.')
    
    return render(request, 'accounts/verify_email.html')

def send_verification_email(user):
    """Send email verification link to user."""
    settings = user.account_settings
    token = get_random_string(32)
    settings.email_verification_token = token
    settings.save()
    
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_email')
    ) + f'?token={token}'
    
    send_mail(
        'Verify your email address',
        f'Please click the following link to verify your email address:\n\n{verification_url}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
