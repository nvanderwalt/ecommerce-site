import stripe
import logging
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Product
from .models import Order

logger = logging.getLogger(__name__)

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            
            # Create a pending order (handle anonymous users)
            user = request.user if request.user.is_authenticated else None
            order = Order.objects.create(
                user=user,
                product=product,
                amount=product.price,
                status='PENDING'
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
        logger.info(f"Order {order_id} completed successfully")
        messages.success(request, "Payment successful! Thank you for your purchase.")
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
