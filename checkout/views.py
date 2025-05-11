import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from inventory.models import Product

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Set Stripe secret key
            stripe.api_key = settings.STRIPE_SECRET_KEY
            print("Stripe secret key in use:", stripe.api_key)

            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(product.price * 100),  # Price in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )

            return redirect(checkout_session.url)

        except stripe.error.AuthenticationError as e:
            print("Stripe Authentication Error:", e)
            return redirect('/error/')
        except Exception as e:
            print("Unexpected Checkout Error:", e)
            return redirect('/error/')
