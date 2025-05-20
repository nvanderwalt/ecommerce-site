from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import SubscriptionPlan, UserSubscription
from django.utils import timezone
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import logging
from django.contrib.auth import get_user_model
from .utils import (
    send_subscription_confirmation,
    send_subscription_cancelled,
    send_payment_failed,
    send_subscription_renewed
)

# Configure logger
logger = logging.getLogger(__name__)
User = get_user_model()

# Create your views here.

class SubscriptionPlanListView(ListView):
    """Display all available subscription plans."""
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        """Return only active subscription plans."""
        return SubscriptionPlan.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_subscription'] = UserSubscription.objects.filter(
                user=self.request.user,
                status='ACTIVE',
                end_date__gt=timezone.now()
            ).first()
        return context

class SubscriptionPlanDetailView(DetailView):
    """Display detailed information about a specific subscription plan."""
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_detail.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_subscription'] = UserSubscription.objects.filter(
                user=self.request.user,
                status='ACTIVE',
                end_date__gt=timezone.now()
            ).first()
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['debug'] = settings.DEBUG
        return context

class UserSubscriptionView(LoginRequiredMixin, TemplateView):
    """Display and manage user's current subscription."""
    template_name = 'subscriptions/user_subscription.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriptions'] = UserSubscription.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
        context['active_subscription'] = UserSubscription.objects.filter(
            user=self.request.user,
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).first()
        return context

    def post(self, request, *args, **kwargs):
        """Handle subscription cancellation."""
        subscription_id = request.POST.get('subscription_id')
        if subscription_id:
            subscription = get_object_or_404(
                UserSubscription,
                id=subscription_id,
                user=request.user
            )
            subscription.cancel_subscription()
            messages.success(request, 'Your subscription has been cancelled.')
        return redirect('user_subscription')

@csrf_exempt
@login_required
def create_subscription_checkout(request, plan_id):
    """Create a Stripe Checkout Session for subscription.
    
    Args:
        request: The HTTP request
        plan_id: ID of the subscription plan
        
    Returns:
        JsonResponse with session ID or error message
    """
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'This endpoint only accepts POST requests'}, 
            status=405
        )

    try:
        # Validate plan exists and is active
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        if not plan.is_active:
            return JsonResponse(
                {'error': 'This subscription plan is no longer available'},
                status=400
            )

        # Check if user already has an active subscription
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).first()

        if active_subscription:
            return JsonResponse(
                {'error': 'You already have an active subscription'},
                status=400
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(plan.price * 100),
                    'product_data': {
                        'name': plan.name,
                        'description': plan.description
                    },
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/subscriptions/success/'),
            cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
            metadata={
                'plan_id': str(plan.id),
                'user_id': str(request.user.id)
            }
        )

        return JsonResponse({'id': checkout_session.id})

    except SubscriptionPlan.DoesNotExist:
        return JsonResponse(
            {'error': 'Subscription plan not found'},
            status=404
        )
    except stripe.error.AuthenticationError:
        return JsonResponse(
            {'error': 'Failed to authenticate with Stripe. Please check your API keys'},
            status=401
        )
    except stripe.error.InvalidRequestError as e:
        return JsonResponse(
            {'error': str(e)},
            status=400
        )
    except stripe.error.RateLimitError:
        return JsonResponse(
            {'error': 'Too many requests to Stripe. Please try again in a moment'},
            status=429
        )
    except stripe.error.StripeError as e:
        return JsonResponse(
            {'error': f'An error occurred with Stripe: {str(e)}'},
            status=400
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f'Unexpected error in create_subscription_checkout: {str(e)}')
        return JsonResponse(
            {'error': 'An unexpected error occurred. Please try again later'},
            status=500
        )

@login_required
def subscription_success(request):
    """Handle successful subscription checkout.
    
    Verifies the subscription was created and shows appropriate success message.
    Redirects to subscription management page.
    """
    try:
        # Get user's most recent subscription
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).order_by('-created_at').first()

        if subscription:
            messages.success(
                request,
                f"Your subscription to the {subscription.plan.name} plan has been activated successfully! "
                "You can manage your subscription from this page."
            )
        else:
            # If no subscription found, might be a delay in webhook processing
            messages.info(
                request,
                "Your subscription is being processed. "
                "This may take a few moments. Please refresh the page."
            )
            
    except Exception as e:
        messages.error(
            request,
            "There was an issue verifying your subscription. "
            "If this persists, please contact support."
        )
        
    return redirect('subscriptions:user_subscription')

@login_required
def subscription_cancel(request):
    """Handle cancelled subscription checkout.
    
    Provides appropriate feedback when user cancels the checkout process.
    Redirects back to plan selection.
    """
    try:
        # Check if user has any pending subscriptions
        pending_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='PENDING'
        ).order_by('-created_at').first()
        
        if pending_subscription:
            # Clean up any pending subscription
            pending_subscription.status = 'CANCELLED'
            pending_subscription.save()
            
        messages.info(
            request,
            "The subscription process was cancelled. "
            "You can choose a different plan or try again later."
        )
            
    except Exception as e:
        messages.error(
            request,
            "There was an issue processing your cancellation. "
            "If you continue to see pending charges, please contact support."
        )
        
    return redirect('subscriptions:plan_list')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Handle subscription creation
            if session.mode == 'subscription':
                plan_id = session.metadata.get('plan_id')
                user_id = session.metadata.get('user_id')
                subscription_id = session.subscription

                try:
                    plan = SubscriptionPlan.objects.get(id=plan_id)
                    user = User.objects.get(id=user_id)
                    
                    # Calculate end date based on plan duration
                    end_date = timezone.now() + timedelta(days=30 * plan.duration_months)
                    
                    # Create user subscription
                    subscription = UserSubscription.objects.create(
                        user=user,
                        plan=plan,
                        status='ACTIVE',
                        start_date=timezone.now(),
                        end_date=end_date,
                        stripe_subscription_id=subscription_id,
                        is_auto_renewal=True
                    )

                    # Send confirmation email
                    send_subscription_confirmation(user, subscription)
                    
                    logger.info(f"Successfully created subscription for user {user.email}")

                except (SubscriptionPlan.DoesNotExist, User.DoesNotExist) as e:
                    logger.error(f"Failed to create subscription: {str(e)}")
                    return HttpResponse(status=400)
                except Exception as e:
                    logger.error(f"Unexpected error creating subscription: {str(e)}")
                    return HttpResponse(status=500)

        elif event['type'] == 'customer.subscription.deleted':
            subscription_id = event['data']['object'].id
            try:
                subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                subscription.cancel_subscription()
                
                # Send cancellation email
                send_subscription_cancelled(subscription.user, subscription)
                
                logger.info(f"Successfully cancelled subscription for user {subscription.user.email}")

            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription not found for ID: {subscription_id}")
            except Exception as e:
                logger.error(f"Error cancelling subscription: {str(e)}")
                return HttpResponse(status=500)

        elif event['type'] == 'invoice.payment_failed':
            subscription_id = event['data']['object'].subscription
            try:
                subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                subscription.status = 'PAYMENT_FAILED'
                subscription.save()
                
                # Send payment failed email
                send_payment_failed(subscription.user, subscription)
                
                logger.warning(f"Payment failed for subscription: {subscription_id}")

            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription not found for failed payment: {subscription_id}")
            except Exception as e:
                logger.error(f"Error handling payment failure: {str(e)}")
                return HttpResponse(status=500)

        elif event['type'] == 'customer.subscription.updated':
            subscription_id = event['data']['object'].id
            try:
                subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Update subscription end date
                current_period_end = event['data']['object'].current_period_end
                subscription.end_date = timezone.datetime.fromtimestamp(
                    current_period_end, 
                    tz=timezone.utc
                )
                subscription.save()
                
                # Send renewal email if this was a renewal
                if event['data']['object'].status == 'active':
                    send_subscription_renewed(subscription.user, subscription)
                
                logger.info(f"Successfully updated subscription: {subscription_id}")

            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription not found for update: {subscription_id}")
            except Exception as e:
                logger.error(f"Error updating subscription: {str(e)}")
                return HttpResponse(status=500)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {str(e)}")
        return HttpResponse(status=500)

@csrf_exempt
@login_required
def switch_subscription_plan(request, plan_id):
    """Handle subscription plan switching.
    
    Args:
        request: The HTTP request
        plan_id: ID of the new subscription plan
        
    Returns:
        JsonResponse with session ID or error message
    """
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'This endpoint only accepts POST requests'}, 
            status=405
        )

    try:
        # Get current active subscription
        current_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).first()

        if not current_subscription:
            return JsonResponse(
                {'error': 'No active subscription found'},
                status=400
            )

        # Get new plan
        new_plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        if not new_plan.is_active:
            return JsonResponse(
                {'error': 'This subscription plan is no longer available'},
                status=400
            )

        # Check if trying to switch to the same plan
        if current_subscription.plan == new_plan:
            return JsonResponse(
                {'error': 'You are already subscribed to this plan'},
                status=400
            )

        # Initiate plan switch
        if not current_subscription.switch_plan(new_plan):
            return JsonResponse(
                {'error': 'Failed to initiate plan switch'},
                status=400
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create Stripe Checkout Session for plan switch
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(new_plan.price * 100),
                    'product_data': {
                        'name': f"Switch to {new_plan.name}",
                        'description': f"Upgrade from {current_subscription.plan.name} to {new_plan.name}"
                    },
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/subscriptions/success/'),
            cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
            metadata={
                'plan_id': str(new_plan.id),
                'user_id': str(request.user.id),
                'current_subscription_id': str(current_subscription.id),
                'is_plan_switch': 'true'
            }
        )

        return JsonResponse({'id': checkout_session.id})

    except SubscriptionPlan.DoesNotExist:
        return JsonResponse(
            {'error': 'Subscription plan not found'},
            status=404
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during plan switch: {str(e)}")
        return JsonResponse(
            {'error': f'An error occurred with Stripe: {str(e)}'},
            status=400
        )
    except Exception as e:
        logger.error(f"Unexpected error during plan switch: {str(e)}")
        return JsonResponse(
            {'error': 'An unexpected error occurred. Please try again later'},
            status=500
        )
