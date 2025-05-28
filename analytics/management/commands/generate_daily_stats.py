from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.contrib.auth.models import User
from analytics.models import SiteStatistics, ProductAnalytics, SubscriptionAnalytics, UserActivity
from inventory.models import Product
from subscriptions.models import SubscriptionPlan, UserSubscription
from checkout.models import Order

class Command(BaseCommand):
    help = 'Generate daily statistics for the site'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Generate site-wide statistics
        self._generate_site_statistics(today)
        
        # Generate product analytics
        self._generate_product_analytics(today)
        
        # Generate subscription analytics
        self._generate_subscription_analytics(today)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated daily statistics'))

    def _generate_site_statistics(self, date):
        """Generate site-wide statistics for the given date."""
        # Get user statistics
        total_users = User.objects.count()
        active_users = UserActivity.objects.filter(
            timestamp__date=date
        ).values('user').distinct().count()
        new_users = User.objects.filter(
            date_joined__date=date
        ).count()
        
        # Get order statistics
        orders = Order.objects.filter(created_at__date=date)
        total_orders = orders.count()
        total_revenue = orders.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get subscription statistics
        subscriptions = UserSubscription.objects.filter(
            created_at__date=date
        )
        active_subscriptions = UserSubscription.objects.filter(
            status='ACTIVE',
            end_date__gt=timezone.now()
        ).count()
        new_subscriptions = subscriptions.filter(
            status='ACTIVE'
        ).count()
        cancelled_subscriptions = subscriptions.filter(
            status='CANCELLED'
        ).count()
        trial_conversions = subscriptions.filter(
            is_trial=False,
            status='ACTIVE'
        ).count()
        
        # Create or update statistics
        SiteStatistics.objects.update_or_create(
            date=date,
            defaults={
                'total_users': total_users,
                'active_users': active_users,
                'new_users': new_users,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'active_subscriptions': active_subscriptions,
                'new_subscriptions': new_subscriptions,
                'cancelled_subscriptions': cancelled_subscriptions,
                'trial_conversions': trial_conversions,
            }
        )

    def _generate_product_analytics(self, date):
        """Generate product-specific analytics for the given date."""
        for product in Product.objects.all():
            # Get product views
            views = UserActivity.objects.filter(
                activity_type='VIEW_PRODUCT',
                content_type__model='product',
                object_id=product.id,
                timestamp__date=date
            ).count()
            
            # Get add to cart actions
            add_to_cart = UserActivity.objects.filter(
                activity_type='ADD_TO_CART',
                content_type__model='product',
                object_id=product.id,
                timestamp__date=date
            ).count()
            
            # Get purchases
            purchases = Order.objects.filter(
                product=product,
                created_at__date=date,
                status='COMPLETED'
            ).count()
            
            # Calculate revenue
            revenue = Order.objects.filter(
                product=product,
                created_at__date=date,
                status='COMPLETED'
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Calculate average rating
            average_rating = product.reviews.filter(
                created_at__date=date
            ).aggregate(
                avg=Avg('rating')
            )['avg'] or 0
            
            # Create or update analytics
            ProductAnalytics.objects.update_or_create(
                product=product,
                date=date,
                defaults={
                    'views': views,
                    'add_to_cart': add_to_cart,
                    'purchases': purchases,
                    'revenue': revenue,
                    'average_rating': average_rating,
                }
            )

    def _generate_subscription_analytics(self, date):
        """Generate subscription-specific analytics for the given date."""
        for plan in SubscriptionPlan.objects.all():
            # Get subscription statistics
            active_subscriptions = UserSubscription.objects.filter(
                plan=plan,
                status='ACTIVE',
                end_date__gt=timezone.now()
            ).count()
            
            new_subscriptions = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                status='ACTIVE'
            ).count()
            
            cancellations = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                status='CANCELLED'
            ).count()
            
            renewals = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                status='ACTIVE'
            ).exclude(
                created_at__date=date
            ).count()
            
            # Calculate revenue
            revenue = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                status='ACTIVE'
            ).aggregate(
                total=Sum('plan__price')
            )['total'] or 0
            
            # Get trial statistics
            trial_starts = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                is_trial=True
            ).count()
            
            trial_conversions = UserSubscription.objects.filter(
                plan=plan,
                created_at__date=date,
                is_trial=False,
                status='ACTIVE'
            ).count()
            
            # Create or update analytics
            SubscriptionAnalytics.objects.update_or_create(
                plan=plan,
                date=date,
                defaults={
                    'active_subscriptions': active_subscriptions,
                    'new_subscriptions': new_subscriptions,
                    'cancellations': cancellations,
                    'renewals': renewals,
                    'revenue': revenue,
                    'trial_starts': trial_starts,
                    'trial_conversions': trial_conversions,
                }
            ) 