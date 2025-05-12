import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Product
from .models import Order

class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            
            # Create a pending order
            order = Order.objects.create(
                user=request.user,
                product=product,
                amount=product.price,
                status='PENDING'
            )

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

            return redirect(checkout_session.url)

        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('product_list')
        except stripe.error.AuthenticationError:
            messages.error(request, "Payment authentication failed. Please try again.")
            return redirect('checkout_error')
        except stripe.error.CardError:
            messages.error(request, "Your card was declined. Please try again with a different card.")
            return redirect('checkout_error')
        except Exception as e:
            messages.error(request, "An unexpected error occurred. Our team has been notified.")
            return redirect('checkout_error')

def success_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'COMPLETED'
        order.save()
        messages.success(request, "Payment successful! Thank you for your purchase.")
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
    return redirect('order_confirmation')

def cancel_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'CANCELLED'
        order.save()
        messages.info(request, "Your order has been cancelled.")
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
    return redirect('product_list')
