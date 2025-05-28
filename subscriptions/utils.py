from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from django.utils import timezone
from datetime import timedelta
from django.utils.html import strip_tags

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

def generate_invoice_pdf(payment_record):
    """
    Generate a professional PDF invoice for a payment record.
    
    Args:
        payment_record: PaymentRecord instance
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create invoices directory if it doesn't exist
    invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)
    
    # Generate PDF filename
    pdf_filename = f"invoice_{payment_record.invoice_number}.pdf"
    pdf_path = os.path.join(invoice_dir, pdf_filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for PDF elements
    elements = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    
    # Add company information with logo
    elements.append(Paragraph("FitFusion", title_style))
    elements.append(Paragraph("123 Fitness Street", styles["Normal"]))
    elements.append(Paragraph("Fitness City, FC 12345", styles["Normal"]))
    elements.append(Paragraph("Phone: (555) 123-4567", styles["Normal"]))
    elements.append(Paragraph("Email: billing@fitfusion.com", styles["Normal"]))
    elements.append(Spacer(1, 30))
    
    # Add invoice information
    elements.append(Paragraph("INVOICE", styles["Heading1"]))
    elements.append(Paragraph(f"Invoice Number: {payment_record.invoice_number}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {payment_record.payment_date.strftime('%B %d, %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Add customer information
    customer = payment_record.subscription.user
    elements.append(Paragraph("Bill To:", styles["Heading3"]))
    elements.append(Paragraph(customer.get_full_name() or customer.email, styles["Normal"]))
    elements.append(Paragraph(customer.email, styles["Normal"]))
    if hasattr(customer, 'profile') and customer.profile.address:
        elements.append(Paragraph(customer.profile.address, styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Add payment details
    data = [
        ['Description', 'Amount'],
        [f"Subscription: {payment_record.subscription.plan.name}", f"${payment_record.amount}"],
        ['', ''],
        ['Subtotal', f"${payment_record.amount}"],
        ['Tax (0%)', '$0.00'],
        ['Total', f"${payment_record.amount}"]
    ]
    
    # Create the table with enhanced styling
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Add payment status and details
    elements.append(Paragraph("Payment Information", styles["Heading3"]))
    elements.append(Paragraph(f"Status: {payment_record.get_status_display()}", styles["Normal"]))
    if payment_record.stripe_payment_id:
        elements.append(Paragraph(f"Payment ID: {payment_record.stripe_payment_id}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Add terms and conditions
    elements.append(Paragraph("Terms & Conditions", styles["Heading3"]))
    elements.append(Paragraph(
        "This invoice is automatically generated and is valid without signature. "
        "Payment is due upon receipt. For any questions regarding this invoice, "
        "please contact our billing department.",
        styles["Normal"]
    ))
    
    # Add footer
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(
        "Thank you for your business!",
        ParagraphStyle(
            'Footer',
            parent=styles["Normal"],
            alignment=1,
            textColor=colors.HexColor('#7f8c8d')
        )
    ))
    
    # Build the PDF
    doc.build(elements)
    
    # Update the payment record with the PDF file
    payment_record.invoice_pdf = f'invoices/{pdf_filename}'
    payment_record.save()
    
    return pdf_path

def send_trial_started_email(user, subscription):
    """Send email notification when a trial period starts."""
    try:
        subject = f"Your {subscription.plan.name} Trial Has Started!"
        html_message = render_to_string('subscriptions/emails/trial_started.html', {
            'user': user,
            'subscription': subscription,
            'trial_end_date': subscription.trial_end_date,
            'days_remaining': subscription.get_trial_remaining_days()
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        logger.info(f"Trial started email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send trial started email: {str(e)}")

def send_trial_reminder_email(user, subscription, days_remaining):
    """Send reminder email before trial period ends."""
    try:
        subject = f"Your {subscription.plan.name} Trial Ends in {days_remaining} Days"
        html_message = render_to_string('subscriptions/emails/trial_reminder.html', {
            'user': user,
            'subscription': subscription,
            'days_remaining': days_remaining,
            'trial_end_date': subscription.trial_end_date
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        logger.info(f"Trial reminder email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send trial reminder email: {str(e)}")

def send_trial_ended_email(user, subscription):
    """Send email notification when a trial period ends."""
    try:
        subject = f"Your {subscription.plan.name} Trial Has Ended"
        html_message = render_to_string('subscriptions/emails/trial_ended.html', {
            'user': user,
            'subscription': subscription,
            'plan': subscription.plan
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        logger.info(f"Trial ended email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send trial ended email: {str(e)}")

def check_trial_notifications():
    """Check and send trial notifications for all active trials."""
    from .models import UserSubscription
    
    # Get all active trials
    active_trials = UserSubscription.objects.filter(
        is_trial=True,
        trial_end_date__gt=timezone.now()
    )
    
    for subscription in active_trials:
        days_remaining = subscription.get_trial_remaining_days()
        
        # Send reminder at 3 days and 1 day before end
        if days_remaining in [3, 1]:
            send_trial_reminder_email(subscription.user, subscription, days_remaining)
    
    # Get trials that ended today
    ended_trials = UserSubscription.objects.filter(
        is_trial=True,
        trial_end_date__date=timezone.now().date()
    )
    
    for subscription in ended_trials:
        send_trial_ended_email(subscription.user, subscription) 