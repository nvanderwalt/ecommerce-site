from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from .forms import NewsletterForm
from .models import Newsletter

def subscribe_newsletter(request):
    """Handle newsletter subscription with AJAX support"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to FitFusion Newsletter!',
                    f'Hi there!\n\nThank you for subscribing to the FitFusion newsletter! You\'ll now receive weekly fitness tips, workout plans, and exclusive offers.\n\nStay motivated and keep pushing towards your fitness goals!\n\nBest regards,\nThe FitFusion Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [newsletter.email],
                    fail_silently=True,  # Don't break the subscription if email fails
                )
            except Exception as e:
                # Log the error but don't break the subscription
                print(f"Failed to send welcome email to {newsletter.email}: {e}")
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter! Check your email for a welcome message.'
                })
            else:
                messages.success(request, 'Thank you for subscribing to our newsletter! Check your email for a welcome message.')
                return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            else:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('home')
    
    return redirect('home')
