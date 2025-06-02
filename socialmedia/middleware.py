"""
Custom middleware for the social media application.
"""
import re
from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve

class AdminStaticFilesMiddleware:
    """
    Middleware to serve admin static files in production.
    This is a workaround for serving admin static files when DEBUG is False.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex for admin static files
        self.admin_static_regex = re.compile(r'^/static/admin/(.*)$')
        # Also match the admin CSS and JS files directly
        self.admin_css_regex = re.compile(r'^/admin/css/(.*)$')
        self.admin_js_regex = re.compile(r'^/admin/js/(.*)$')
        self.admin_img_regex = re.compile(r'^/admin/img/(.*)$')
        
    def __call__(self, request):
        # Check if the request is for admin static files
        match = self.admin_static_regex.match(request.path)
        if match:
            # Extract the path to the static file
            path = match.group(1)
            # Try to serve from STATIC_ROOT first
            try:
                return serve(request, path, document_root=settings.STATIC_ROOT + '/admin/')
            except:
                # If that fails, try to serve from Django's admin app
                import django
                django_path = django.__path__[0]
                return serve(request, path, document_root=django_path + '/contrib/admin/static/admin/')
        
        # Check for direct admin asset requests
        css_match = self.admin_css_regex.match(request.path)
        if css_match:
            path = css_match.group(1)
            import django
            django_path = django.__path__[0]
            return serve(request, path, document_root=django_path + '/contrib/admin/static/admin/css/')
            
        js_match = self.admin_js_regex.match(request.path)
        if js_match:
            path = js_match.group(1)
            import django
            django_path = django.__path__[0]
            return serve(request, path, document_root=django_path + '/contrib/admin/static/admin/js/')
            
        img_match = self.admin_img_regex.match(request.path)
        if img_match:
            path = img_match.group(1)
            import django
            django_path = django.__path__[0]
            return serve(request, path, document_root=django_path + '/contrib/admin/static/admin/img/')
        
        # Continue with normal request processing
        return self.get_response(request)
