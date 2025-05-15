from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_subscription_email(user, subject, template_name, context):
    """
    Send an email to a user using a specified template.
    
    Args:
        user: The user to send the email to
        subject: Email subject
        template_name: Name of the template to use
        context: Dictionary containing template context
    """
    try:
        # Add user to context
        context['user'] = user
        
        # Render HTML message
        html_message = render_to_string(f'subscriptions/emails/{template_name}.html', context)
        
        # Render text message
        text_message = render_to_string(f'subscriptions/emails/{template_name}.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Successfully sent {template_name} email to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send {template_name} email to {user.email}: {str(e)}")
        raise

def send_subscription_confirmation(user, subscription):
    """Send subscription confirmation email."""
    context = {
        'subscription': subscription,
        'plan': subscription.plan,
    }
    send_subscription_email(
        user=user,
        subject='Welcome to FitFusion Premium!',
        template_name='subscription_confirmation',
        context=context
    )

def send_subscription_cancelled(user, subscription):
    """Send subscription cancellation email."""
    context = {
        'subscription': subscription,
        'plan': subscription.plan,
    }
    send_subscription_email(
        user=user,
        subject='Your FitFusion Subscription Has Been Cancelled',
        template_name='subscription_cancelled',
        context=context
    )

def send_payment_failed(user, subscription):
    """Send payment failure notification email."""
    context = {
        'subscription': subscription,
        'plan': subscription.plan,
    }
    send_subscription_email(
        user=user,
        subject='Action Required: Payment Failed',
        template_name='payment_failed',
        context=context
    )

def send_subscription_renewed(user, subscription):
    """Send subscription renewal confirmation email."""
    context = {
        'subscription': subscription,
        'plan': subscription.plan,
    }
    send_subscription_email(
        user=user,
        subject='Your FitFusion Subscription Has Been Renewed',
        template_name='subscription_renewed',
        context=context
    ) 