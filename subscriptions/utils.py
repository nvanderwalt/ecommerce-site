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
    Generate a PDF invoice for a payment record.
    
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
        spaceAfter=30
    )
    
    # Add company information
    elements.append(Paragraph("FitFusion", title_style))
    elements.append(Paragraph("123 Fitness Street", styles["Normal"]))
    elements.append(Paragraph("Fitness City, FC 12345", styles["Normal"]))
    elements.append(Spacer(1, 30))
    
    # Add invoice information
    elements.append(Paragraph(f"Invoice #{payment_record.invoice_number}", styles["Heading2"]))
    elements.append(Paragraph(f"Date: {payment_record.payment_date.strftime('%B %d, %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Add customer information
    customer = payment_record.subscription.user
    elements.append(Paragraph("Bill To:", styles["Heading3"]))
    elements.append(Paragraph(customer.get_full_name() or customer.email, styles["Normal"]))
    elements.append(Paragraph(customer.email, styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Add payment details
    data = [
        ['Description', 'Amount'],
        [f"Subscription: {payment_record.subscription.plan.name}", f"${payment_record.amount}"]
    ]
    
    # Create the table
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Add payment status
    elements.append(Paragraph(f"Status: {payment_record.get_status_display()}", styles["Normal"]))
    if payment_record.stripe_payment_id:
        elements.append(Paragraph(f"Payment ID: {payment_record.stripe_payment_id}", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    
    # Update the payment record with the PDF file
    payment_record.invoice_pdf = f'invoices/{pdf_filename}'
    payment_record.save()
    
    return pdf_path 