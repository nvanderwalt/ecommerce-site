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