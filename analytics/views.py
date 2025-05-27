from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import JsonResponse
from .models import UserActivity, SiteStatistics, ProductAnalytics, SubscriptionAnalytics

def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def analytics_dashboard(request):
    """Main analytics dashboard view."""
    # Get date range (default to last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)
    
    # Get site statistics
    site_stats = SiteStatistics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Get top products
    top_products = ProductAnalytics.objects.filter(
        date__range=[start_date, end_date]
    ).values('product__name').annotate(
        total_views=Sum('views'),
        total_purchases=Sum('purchases'),
        total_revenue=Sum('revenue')
    ).order_by('-total_revenue')[:5]
    
    # Get subscription metrics
    subscription_stats = SubscriptionAnalytics.objects.filter(
        date__range=[start_date, end_date]
    ).values('plan__name').annotate(
        active_subs=Sum('active_subscriptions'),
        new_subs=Sum('new_subscriptions'),
        total_revenue=Sum('revenue')
    ).order_by('-total_revenue')
    
    # Get recent user activities
    recent_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'site_stats': site_stats,
        'top_products': top_products,
        'subscription_stats': subscription_stats,
        'recent_activities': recent_activities,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def activity_logs(request):
    """View for detailed user activity logs."""
    activities = UserActivity.objects.select_related('user').order_by('-timestamp')
    
    # Filter by activity type if provided
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        activities = activities.filter(user_id=user_id)
    
    context = {
        'activities': activities,
        'activity_types': UserActivity.ACTIVITY_TYPES
    }
    
    return render(request, 'analytics/activity_logs.html', context)

@login_required
@user_passes_test(is_staff_user)
def get_analytics_data(request):
    """API endpoint for getting analytics data for charts."""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'Date range required'}, status=400)
    
    # Get site statistics for the date range
    stats = SiteStatistics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    data = {
        'dates': [stat.date.strftime('%Y-%m-%d') for stat in stats],
        'active_users': [stat.active_users for stat in stats],
        'total_orders': [stat.total_orders for stat in stats],
        'total_revenue': [float(stat.total_revenue) for stat in stats]
    }
    
    return JsonResponse(data)
