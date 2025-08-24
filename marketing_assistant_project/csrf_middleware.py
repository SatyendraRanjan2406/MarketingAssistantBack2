from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
import re

class CustomCsrfMiddleware(MiddlewareMixin):
    """
    Custom CSRF middleware that automatically exempts API endpoints
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.csrf_middleware = CsrfViewMiddleware(get_response)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the view has @csrf_exempt decorator
        if getattr(callback, 'csrf_exempt', False):
            return None
        
        # Check if the request is to an API endpoint
        if request.path.startswith('/accounts/api/') or request.path.startswith('/google-ads-new/api/'):
            # For API endpoints, skip CSRF validation
            return None
        
        # For non-API endpoints, use the standard CSRF middleware
        return self.csrf_middleware.process_view(request, callback, callback_args, callback_kwargs)
