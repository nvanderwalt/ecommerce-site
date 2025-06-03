from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.contrib import messages
from django.urls import reverse
from .models import SubscriptionPlan, UserSubscription, PaymentRecord
from django.utils import timezone
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import logging
from django.contrib.auth import get_user_model
from .utils import (
    send_subscription_confirmation,
    send_subscription_cancelled,
    send_payment_failed,
    send_subscription_renewed,
    generate_invoice_pdf,
    send_trial_started_email,
    send_trial_reminder_email,
    send_trial_ended_email
)
from django.db import models

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
                status__in=['ACTIVE', 'TRIAL'],
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
    login_url = reverse

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
        
        # Add available plans for switching
        context['available_plans'] = SubscriptionPlan.objects.filter(
            is_active=True
        ).exclude(
            usersubscription__user=self.request.user,
            usersubscription__status='ACTIVE',
            usersubscription__end_date__gt=timezone.now()
        )
        
        # Add Stripe public key for the template
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        
        return context

    def post(self, request, *args, **kwargs):
        """Handle subscription actions."""
        subscription_id = request.POST.get('subscription_id')
        action = request.POST.get('action')
        
        if not subscription_id:
            messages.error(request, 'Invalid subscription ID')
            return redirect('subscriptions:user_subscription')
            
        subscription = get_object_or_404(
            UserSubscription,
            id=subscription_id,
            user=request.user
        )
        
        if action == 'toggle_renewal':
            # Handle auto-renewal toggle
            auto_renew = request.POST.get('auto_renew') == 'on'
            subscription.auto_renew = auto_renew
            subscription.save()
            
            if auto_renew:
                messages.success(
                    request,
                    'Auto-renewal has been enabled for your subscription.'
                )
            else:
                messages.success(
                    request,
                    'Auto-renewal has been disabled for your subscription.'
                )
        else:
            # Handle cancellation
            immediate = request.POST.get('immediate') == 'true'
            
            if subscription.cancel_subscription(immediate=immediate):
                if immediate:
                    messages.success(
                        request,
                        'Your subscription has been cancelled immediately. '
                        'You will no longer have access to premium features.'
                    )
                else:
                    messages.success(
                        request,
                        'Your subscription has been cancelled. '
                        'You will continue to have access until the end of your billing period.'
                    )
            else:
                messages.error(
                    request,
                    'There was an error cancelling your subscription. '
                    'Please try again or contact support.'
                )
                
        return redirect('subscriptions:user_subscription')

@login_required
def plan_list(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    current_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'subscriptions/plan_list.html', context)

@login_required
def dashboard(request):
    current_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    subscription_history = UserSubscription.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    context = {
        'current_subscription': current_subscription,
        'subscription_history': subscription_history
    }
    return render(request, 'subscriptions/dashboard.html', context)

@login_required
def create_subscription(request, plan_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if user already has an active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if active_subscription:
        return JsonResponse({
            'error': 'You already have an active subscription'
        }, status=400)
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/subscriptions/success/'),
            cancel_url=request.build_absolute_uri('/subscriptions/'),
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id
            }
        )
        
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def subscription_success(request):
    messages.success(request, 'Your subscription has been activated successfully!')
    return redirect('subscriptions:dashboard')

@login_required
def subscription_cancel(request):
    if request.method != 'POST':
        return redirect('subscriptions:dashboard')
    
    subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if subscription:
        subscription.cancel()
        messages.success(request, 'Your subscription has been cancelled.')
    else:
        messages.error(request, 'No active subscription found.')
    
    return redirect('subscriptions:dashboard')

@login_required
def subscription_renew(request):
    if request.method != 'POST':
        return redirect('subscriptions:dashboard')
    
    subscription = UserSubscription.objects.filter(
        user=request.user,
        status='cancelled',
        end_date__gt=timezone.now()
    ).first()
    
    if subscription and subscription.renew():
        messages.success(request, 'Your subscription has been renewed.')
    else:
        messages.error(request, 'Unable to renew subscription.')
    
    return redirect('subscriptions:dashboard')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        handle_checkout_session_completed(session)
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        handle_subscription_updated(subscription)
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        handle_subscription_deleted(subscription)
    elif event.type == 'invoice.payment_succeeded':
        invoice = event.data.object
        handle_invoice_payment_succeeded(invoice)
    elif event.type == 'invoice.payment_failed':
        invoice = event.data.object
        handle_invoice_payment_failed(invoice)
    
    return HttpResponse(status=200)

def handle_checkout_session_completed(session):
    """Handle successful checkout session completion."""
    try:
        # Get the subscription details from the session
        subscription_id = session.subscription
        customer_id = session.customer
        plan_id = session.metadata.get('plan_id')
        user_id = session.metadata.get('user_id')
        
        # Get the subscription from Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Get the user and plan
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Create or update the user's subscription
        user_subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'status': 'ACTIVE',
                'stripe_subscription_id': subscription_id,
                'end_date': timezone.datetime.fromtimestamp(
                    subscription.current_period_end,
                    tz=timezone.utc
                ),
                'auto_renew': True
            }
        )
        
        if not created:
            user_subscription.plan = plan
            user_subscription.status = 'ACTIVE'
            user_subscription.stripe_subscription_id = subscription_id
            user_subscription.end_date = timezone.datetime.fromtimestamp(
                subscription.current_period_end,
                tz=timezone.utc
            )
            user_subscription.auto_renew = True
            user_subscription.save()
        
        # Send confirmation email
        send_subscription_confirmation(user, plan)
        
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}")
        raise

def handle_subscription_updated(subscription):
    """Handle subscription updates from Stripe."""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription.id
        )
        
        if subscription.status == 'active':
            user_subscription.status = 'ACTIVE'
            user_subscription.end_date = timezone.datetime.fromtimestamp(
                subscription.current_period_end,
                tz=timezone.utc
            )
            user_subscription.save()
            send_subscription_renewed(user_subscription.user, user_subscription.plan)
        elif subscription.status == 'canceled':
            user_subscription.status = 'CANCELLED'
            user_subscription.auto_renew = False
            user_subscription.save()
            send_subscription_cancelled(user_subscription.user, user_subscription.plan)
            
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription.id} not found")
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")
        raise

def handle_subscription_deleted(subscription):
    """Handle subscription deletion from Stripe."""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription.id
        )
        user_subscription.status = 'CANCELLED'
        user_subscription.auto_renew = False
        user_subscription.save()
        send_subscription_cancelled(user_subscription.user, user_subscription.plan)
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription.id} not found")
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")
        raise

def handle_invoice_payment_succeeded(invoice):
    """Handle successful invoice payment."""
    try:
        subscription_id = invoice.subscription
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        
        # Create payment record
        PaymentRecord.objects.create(
            subscription=user_subscription,
            amount=invoice.amount_paid / 100,  # Convert from cents
            currency=invoice.currency,
            status='SUCCEEDED',
            stripe_payment_id=invoice.payment_intent,
            invoice_number=invoice.number
        )
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
    except Exception as e:
        logger.error(f"Error handling invoice payment: {str(e)}")
        raise

def handle_invoice_payment_failed(invoice):
    """Handle failed invoice payment."""
    try:
        subscription_id = invoice.subscription
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        
        # Create payment record
        PaymentRecord.objects.create(
            subscription=user_subscription,
            amount=invoice.amount_due / 100,  # Convert from cents
            currency=invoice.currency,
            status='FAILED',
            stripe_payment_id=invoice.payment_intent,
            invoice_number=invoice.number
        )
        
        # Send payment failed notification
        send_payment_failed(user_subscription.user, user_subscription.plan)
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
    except Exception as e:
        logger.error(f"Error handling failed payment: {str(e)}")
        raise

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

@login_required
def payment_history(request):
    """
    Display user's payment history with downloadable invoices.
    Supports filtering by date range and status, and sorting by different fields.
    """
    try:
        # Get all payments for user's subscriptions
        payments = PaymentRecord.objects.filter(
            subscription__user=request.user
        )

        # Apply filters
        status_filter = request.GET.get('status')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        sort_by = request.GET.get('sort', '-payment_date')

        if status_filter:
            payments = payments.filter(status=status_filter)
        if date_from:
            payments = payments.filter(payment_date__gte=date_from)
        if date_to:
            payments = payments.filter(payment_date__lte=date_to)

        # Apply sorting
        payments = payments.order_by(sort_by)

        # Calculate summary statistics
        total_paid = payments.filter(status='SUCCEEDED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        context = {
            'payments': payments,
            'total_paid': total_paid,
            'status_choices': PaymentRecord.PAYMENT_STATUS,
            'current_filters': {
                'status': status_filter,
                'date_from': date_from,
                'date_to': date_to,
                'sort': sort_by
            }
        }
        
        return render(request, 'subscriptions/payment_history.html', context)
        
    except Exception as e:
        logger.error(f"Error in payment history view: {str(e)}")
        messages.error(request, "An error occurred while loading payment history.")
        return redirect('subscriptions:dashboard')

@login_required
def download_invoice(request, payment_id):
    """
    Download invoice PDF for a specific payment.
    """
    try:
        payment = get_object_or_404(
            PaymentRecord,
            id=payment_id,
            subscription__user=request.user
        )
        
        if not payment.invoice_pdf:
            # Generate PDF if it doesn't exist
            generate_invoice_pdf(payment)
        
        # Serve the PDF file
        response = FileResponse(
            payment.invoice_pdf,
            as_attachment=True,
            filename=f"invoice_{payment.invoice_number}.pdf"
        )
        return response
        
    except Exception as e:
        logger.error(f"Error downloading invoice: {str(e)}")
        messages.error(request, "An error occurred while downloading the invoice.")
        return redirect('subscriptions:payment_history')

@login_required
def start_trial(request, plan_id):
    """Start a trial period for a subscription plan.
    
    Args:
        request: The HTTP request
        plan_id: ID of the subscription plan
        
    Returns:
        Redirect to subscription page with success/error message
    """
    try:
        # Validate plan exists and is active
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        if not plan.is_active:
            logger.warning(f"Attempted to start trial for inactive plan {plan_id}")
            messages.error(request, 'This subscription plan is no longer available')
            return redirect('subscriptions:plan_list')

        # Check if user already has an active subscription or trial
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            status__in=['ACTIVE', 'TRIAL'],
            end_date__gt=timezone.now()
        ).first()

        if active_subscription:
            if active_subscription.is_trial_active():
                logger.info(f"User {request.user.id} attempted to start trial while having active trial")
                messages.error(request, 'You already have an active trial subscription')
            else:
                logger.info(f"User {request.user.id} attempted to start trial while having active subscription")
                messages.error(request, 'You already have an active subscription')
            return redirect('subscriptions:plan_list')

        # Check if user has used a trial before
        has_used_trial = UserSubscription.objects.filter(
            user=request.user,
            is_trial=True
        ).exists()

        if has_used_trial:
            logger.info(f"User {request.user.id} attempted to start trial after using one before")
            messages.error(request, 'You have already used your trial period')
            return redirect('subscriptions:plan_list')

        # Create new subscription with trial
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            status='TRIAL',
            end_date=timezone.now() + timezone.timedelta(days=14),
            is_trial=True,
            trial_end_date=timezone.now() + timezone.timedelta(days=14)
        )

        # Send trial started email
        try:
            send_trial_started_email(request.user, subscription)
        except Exception as e:
            logger.error(f"Failed to send trial started email to user {request.user.id}: {str(e)}")

        # Schedule trial reminder emails
        reminder_days = [3, 1]  # Send reminders 3 days and 1 day before trial ends
        for days in reminder_days:
            reminder_date = subscription.trial_end_date - timezone.timedelta(days=days)
            if reminder_date > timezone.now():
                try:
                    send_trial_reminder_email(request.user, subscription, days)
                except Exception as e:
                    logger.error(f"Failed to send trial reminder email to user {request.user.id}: {str(e)}")

        logger.info(f"Successfully started trial for user {request.user.id} with plan {plan_id}")
        messages.success(
            request,
            'Your trial period has started. You have 14 days to try out our premium features.'
        )
        return redirect('subscriptions:user_subscription')

    except Exception as e:
        logger.error(f"Error starting trial for user {request.user.id}: {str(e)}")
        messages.error(
            request,
            'There was an error starting your trial. Please try again or contact support.'
        )
        return redirect('subscriptions:plan_list')

@login_required
def convert_trial(request, subscription_id):
    """Convert a trial subscription to a paid subscription."""
    try:
        subscription = get_object_or_404(
            UserSubscription,
            id=subscription_id,
            user=request.user,
            is_trial=True
        )
        
        if not subscription.is_trial_active():
            logger.warning(f"User {request.user.id} attempted to convert expired trial")
            messages.error(request, 'Your trial period has expired.')
            return redirect('subscriptions:plan_list')
        
        # Record conversion in usage stats if they exist
        if hasattr(subscription, 'usage_stats'):
            subscription.usage_stats.record_conversion()
        
        # Create Stripe Checkout Session for conversion
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(subscription.plan.price * 100),
                        'product_data': {
                            'name': subscription.plan.name,
                            'description': subscription.plan.description
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
                    'plan_id': str(subscription.plan.id),
                    'user_id': str(request.user.id),
                    'is_trial_conversion': 'true',
                    'trial_subscription_id': str(subscription.id)
                }
            )
            
            logger.info(f"Created checkout session for trial conversion: user {request.user.id}")
            return JsonResponse({'id': checkout_session.id})
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during trial conversion: {str(e)}")
            messages.error(request, 'An error occurred while processing your payment. Please try again.')
            return redirect('subscriptions:user_subscription')
            
    except UserSubscription.DoesNotExist:
        logger.warning(f"Attempted to convert non-existent trial subscription {subscription_id}")
        messages.error(request, 'Invalid subscription.')
        return redirect('subscriptions:plan_list')
    except Exception as e:
        logger.error(f"Error converting trial: {str(e)}")
        messages.error(request, 'An error occurred while processing your request.')
        return redirect('subscriptions:user_subscription')
