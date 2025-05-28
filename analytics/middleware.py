from django.utils import timezone
from .models import UserActivity

class UserActivityMiddleware:
    """Middleware to track user activities."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only track activities for authenticated users
        if request.user.is_authenticated:
            self._track_activity(request)
        
        return response
    
    def _track_activity(self, request):
        """Track user activity based on the request."""
        activity_type = self._get_activity_type(request)
        if not activity_type:
            return
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Create activity record
        UserActivity.objects.create(
            user=request.user,
            activity_type=activity_type,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata=self._get_activity_metadata(request)
        )
    
    def _get_activity_type(self, request):
        """Determine activity type based on request path and method."""
        path = request.path.lower()
        method = request.method
        
        # Login/Logout
        if path.endswith('/login/') and method == 'POST':
            return 'LOGIN'
        elif path.endswith('/logout/') and method == 'POST':
            return 'LOGOUT'
        
        # Product related
        elif '/product/' in path and method == 'GET':
            return 'VIEW_PRODUCT'
        elif '/cart/add/' in path and method == 'POST':
            return 'ADD_TO_CART'
        elif '/cart/remove/' in path and method == 'POST':
            return 'REMOVE_FROM_CART'
        
        # Checkout
        elif '/checkout/' in path and method == 'POST':
            return 'CHECKOUT'
        
        # Subscription related
        elif '/subscription/start/' in path and method == 'POST':
            return 'SUBSCRIPTION_START'
        elif '/subscription/cancel/' in path and method == 'POST':
            return 'SUBSCRIPTION_CANCEL'
        elif '/subscription/renew/' in path and method == 'POST':
            return 'SUBSCRIPTION_RENEW'
        elif '/subscription/switch/' in path and method == 'POST':
            return 'PLAN_SWITCH'
        elif '/subscription/trial/start/' in path and method == 'POST':
            return 'TRIAL_START'
        elif '/subscription/trial/convert/' in path and method == 'POST':
            return 'TRIAL_CONVERT'
        
        return None
    
    def _get_activity_metadata(self, request):
        """Extract relevant metadata from the request."""
        metadata = {}
        
        # Add product ID if viewing a product
        if '/product/' in request.path.lower():
            try:
                product_id = request.path.split('/')[-2]
                metadata['product_id'] = product_id
            except (IndexError, ValueError):
                pass
        
        # Add subscription plan ID if subscription related
        if '/subscription/' in request.path.lower():
            try:
                plan_id = request.POST.get('plan_id')
                if plan_id:
                    metadata['plan_id'] = plan_id
            except (AttributeError, ValueError):
                pass
        
        return metadata 