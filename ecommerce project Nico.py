def _handle_checkout_session_completed(session):
    """Handle completed checkout session event.
    
    Args:
        session: Stripe checkout session object
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        if session.mode != 'subscription':
            return True, None
            
        plan_id = session.metadata.get('plan_id')
        user_id = session.metadata.get('user_id')
        subscription_id = session.subscription
        is_plan_switch = session.metadata.get('is_plan_switch') == 'true'

        plan = SubscriptionPlan.objects.get(id=plan_id)
        user = User.objects.get(id=user_id)
        
        if is_plan_switch:
            current_subscription_id = session.metadata.get('current_subscription_id')
            current_subscription = UserSubscription.objects.get(
                id=current_subscription_id,
                user=user,
                status='SWITCHING'
            )
            
            current_subscription.status = 'CANCELLED'
            current_subscription.save()
            
            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                status='ACTIVE',
                start_date=timezone.now(),
                end_date=current_subscription.end_date,
                stripe_subscription_id=subscription_id,
                is_auto_renewal=True
            )
            
            logger.info(f"Successfully switched plan for user {user.email}")
        else:
            end_date = timezone.now() + timedelta(days=30 * plan.duration_months)
            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                status='ACTIVE',
                start_date=timezone.now(),
                end_date=end_date,
                stripe_subscription_id=subscription_id,
                is_auto_renewal=True
            )
            logger.info(f"Successfully created subscription for user {user.email}")

        send_subscription_confirmation(user, subscription)
        return True, None

    except (SubscriptionPlan.DoesNotExist, User.DoesNotExist) as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error creating subscription: {str(e)}")
        return False, str(e)

def _handle_subscription_deleted(subscription_id):
    """Handle subscription deletion event.
    
    Args:
        subscription_id: Stripe subscription ID
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        subscription.cancel_subscription()
        
        send_subscription_cancelled(subscription.user, subscription)
        logger.info(f"Successfully cancelled subscription for user {subscription.user.email}")
        return True, None

    except UserSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for ID: {subscription_id}")
        return False, "Subscription not found"
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return False, str(e)

def _handle_payment_failed(subscription_id):
    """Handle payment failure event.
    
    Args:
        subscription_id: Stripe subscription ID
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        subscription.status = 'PAYMENT_FAILED'
        subscription.save()
        
        send_payment_failed(subscription.user, subscription)
        logger.warning(f"Payment failed for subscription: {subscription_id}")
        return True, None

    except UserSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for failed payment: {subscription_id}")
        return False, "Subscription not found"
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")
        return False, str(e)

def _handle_subscription_updated(subscription_id, event_data):
    """Handle subscription update event.
    
    Args:
        subscription_id: Stripe subscription ID
        event_data: Stripe event data object
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        
        current_period_end = event_data.current_period_end
        subscription.end_date = timezone.datetime.fromtimestamp(
            current_period_end, 
            tz=timezone.utc
        )
        subscription.save()
        
        if event_data.status == 'active':
            send_subscription_renewed(subscription.user, subscription)
        
        logger.info(f"Successfully updated subscription: {subscription_id}")
        return True, None

    except UserSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for update: {subscription_id}")
        return False, "Subscription not found"
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        return False, str(e)

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
        event_type = event['type']
        event_data = event['data']['object']

        if event_type == 'checkout.session.completed':
            success, error = _handle_checkout_session_completed(event_data)
        elif event_type == 'customer.subscription.deleted':
            success, error = _handle_subscription_deleted(event_data.id)
        elif event_type == 'invoice.payment_failed':
            success, error = _handle_payment_failed(event_data.subscription)
        elif event_type == 'customer.subscription.updated':
            success, error = _handle_subscription_updated(event_data.id, event_data)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return HttpResponse(status=200)

        if not success:
            logger.error(f"Error handling {event_type}: {error}")
            return HttpResponse(status=500)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {str(e)}")
        return HttpResponse(status=500)

class SubscriptionPlanListView(ListView):
    """Display all available subscription plans.
    
    This view shows a list of all active subscription plans available to users.
    For authenticated users, it also shows their current active subscription if any.
    
    Attributes:
        model: The SubscriptionPlan model to use
        template_name: The template to render
        context_object_name: The name to use for the plans in the template
        
    Template Context:
        plans: List of active subscription plans
        current_subscription: User's active subscription (if authenticated)
    """
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        """Return only active subscription plans.
        
        Returns:
            QuerySet: Filtered queryset containing only active plans
        """
        return SubscriptionPlan.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        """Add current subscription to context if user is authenticated.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context data including plans and current subscription
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_subscription'] = UserSubscription.objects.filter(
                user=self.request.user,
                status='ACTIVE',
                end_date__gt=timezone.now()
            ).first()
        return context

class SubscriptionPlanDetailView(DetailView):
    """Display detailed information about a specific subscription plan.
    
    This view shows detailed information about a specific subscription plan,
    including pricing, features, and subscription options. For authenticated users,
    it also shows their current subscription status.
    
    Attributes:
        model: The SubscriptionPlan model to use
        template_name: The template to render
        context_object_name: The name to use for the plan in the template
        
    Template Context:
        plan: The subscription plan being viewed
        current_subscription: User's active subscription (if authenticated)
        stripe_public_key: Stripe public key for payment integration
        debug: Debug mode status
    """
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_detail.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        """Add additional context data for the template.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context data including plan details and Stripe configuration
        """
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
    """Display and manage user's current subscription.
    
    This view allows users to view and manage their subscription details,
    including cancellation, renewal settings, and plan switching options.
    Requires user authentication.
    
    Attributes:
        template_name: The template to render
        login_url: URL to redirect to if user is not authenticated
        
    Template Context:
        subscriptions: List of user's subscription history
        active_subscription: User's current active subscription
        available_plans: List of plans available for switching
        stripe_public_key: Stripe public key for payment integration
    """
    template_name = 'subscriptions/user_subscription.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        """Add subscription data to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context data including subscription details and available plans
        """
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
        
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self, request, *args, **kwargs):
        """Handle subscription management actions.
        
        Processes subscription-related actions like cancellation and auto-renewal
        toggling. Validates the subscription belongs to the user before processing.
        
        Args:
            request: The HTTP request
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            HttpResponse: Redirect to subscription management page
            
        Raises:
            Http404: If subscription not found or doesn't belong to user
        """
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