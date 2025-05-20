from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import UserSubscription
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Renews subscriptions that are due for renewal'

    def handle(self, *args, **options):
        # Get subscriptions that are due for renewal (within next 24 hours)
        due_subscriptions = UserSubscription.objects.filter(
            status='ACTIVE',
            end_date__lte=timezone.now() + timezone.timedelta(days=1),
            end_date__gt=timezone.now(),
            auto_renew=True
        )

        renewed_count = 0
        failed_count = 0

        for subscription in due_subscriptions:
            try:
                if subscription.renew_subscription():
                    # Send renewal confirmation email
                    send_mail(
                        'Subscription Renewed',
                        f'Your subscription to {subscription.plan.name} has been renewed successfully.',
                        settings.DEFAULT_FROM_EMAIL,
                        [subscription.user.email],
                        fail_silently=True
                    )
                    renewed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully renewed subscription for {subscription.user.email}'
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Failed to renew subscription for {subscription.user.email}'
                        )
                    )
            except Exception as e:
                logger.error(f'Error renewing subscription: {str(e)}')
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error renewing subscription for {subscription.user.email}: {str(e)}'
                    )
                )

        # Handle expired subscriptions
        expired_subscriptions = UserSubscription.objects.filter(
            status='ACTIVE',
            end_date__lte=timezone.now()
        )

        for subscription in expired_subscriptions:
            try:
                subscription.status = 'EXPIRED'
                subscription.save()
                # Send expiration notification
                send_mail(
                    'Subscription Expired',
                    f'Your subscription to {subscription.plan.name} has expired.',
                    settings.DEFAULT_FROM_EMAIL,
                    [subscription.user.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f'Error handling expired subscription: {str(e)}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Renewal process completed. Renewed: {renewed_count}, Failed: {failed_count}'
            )
        ) 