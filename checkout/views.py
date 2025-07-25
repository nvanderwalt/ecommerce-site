import stripe
import logging
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from inventory.models import Product
from .models import Order

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):
    """Send confirmation email for successful order."""
    try:
        subject = f'Order Confirmation - {order.product.name}'
        
        # Create email content
        context = {
            'order': order,
            'product': order.product,
        }
        
        html_message = render_to_string('checkout/email/order_confirmation.html', context)
        plain_message = f"""
        Thank you for your purchase!
        
        Order ID: {order.id}
        Product: {order.product.name}
        Amount: €{order.amount}
        Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
        
        We'll process your order shortly.
        """
        
        # Determine recipient email
        recipient_email = order.user.email if order.user else order.email
        
        if recipient_email:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Order confirmation email sent to {recipient_email} for order {order.id}")
        else:
            logger.warning(f"No email address found for order {order.id}")
            
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order {order.id}: {str(e)}")

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            
            # Get email from form data for anonymous users
            email = request.POST.get('email', '') if not request.user.is_authenticated else ''
            
            # Create a pending order (handle anonymous users)
            user = request.user if request.user.is_authenticated else None
            order = Order.objects.create(
                user=user,
                product=product,
                amount=product.price,
                status='PENDING',
                email=email
            )
            logger.info(f"Created pending order {order.id} for user {user.username if user else 'anonymous'}")

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/checkout/success/{order.id}/'),
                cancel_url=request.build_absolute_uri(f'/checkout/cancel/{order.id}/'),
                metadata={
                    'order_id': order.id
                }
            )

            # Update order with payment intent
            order.stripe_payment_intent = checkout_session.payment_intent
            order.save()
            logger.info(f"Created Stripe checkout session for order {order.id}")

            return redirect(checkout_session.url)

        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            messages.error(request, "Product not found.")
            return redirect('product_list')
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {str(e)}")
            messages.error(request, "Payment authentication failed. Please try again.")
            return redirect('checkout_error')
        except stripe.error.CardError as e:
            logger.error(f"Stripe card error: {str(e)}")
            messages.error(request, "Your card was declined. Please try again with a different card.")
            return redirect('checkout_error')
        except Exception as e:
            logger.error(f"Unexpected error in checkout: {str(e)}", exc_info=True)
            messages.error(request, "An unexpected error occurred. Our team has been notified.")
            return redirect('checkout_error')

def success_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'COMPLETED'
        order.save()
        
        # Send confirmation email
        send_order_confirmation_email(order)
        
        logger.info(f"Order {order_id} completed successfully")
        messages.success(request, "Payment successful! Thank you for your purchase. A confirmation email has been sent.")
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        messages.error(request, "Order not found.")
    return redirect('order_confirmation')

def cancel_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'CANCELLED'
        order.save()
        logger.info(f"Order {order_id} cancelled")
        messages.info(request, "Your order has been cancelled.")
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        messages.error(request, "Order not found.")
    return redirect('product_list')

def checkout_error(request):
    """View to display checkout errors and provide recovery options."""
    return render(request, 'checkout/error.html', {
        'error_message': messages.get_messages(request),
        'support_email': settings.DEFAULT_FROM_EMAIL
    })
