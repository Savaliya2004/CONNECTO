"""
Middleware for the CONNECTO Admin Dashboard.
Protects all /control/ routes and logs failed access attempts.
"""
from django.shortcuts import redirect
from django.urls import reverse
from .models import AdminActivityLog


class AdminAccessMiddleware:
    """
    Middleware that intercepts all /control/ requests and verifies
    the user is authenticated as a Django staff/superuser.
    Logs failed access attempts to AdminActivityLog.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Only apply to /control/ paths (exclude login page itself)
        if path.startswith('/control/') and not path.startswith('/control/login/'):
            if not request.user.is_authenticated:
                _log_failed_access(request)
                login_url = reverse('admin_dashboard:login')
                return redirect(f'{login_url}?next={path}')

            if not (request.user.is_staff or request.user.is_superuser):
                _log_failed_access(request, request.user)
                login_url = reverse('admin_dashboard:login')
                return redirect(f'{login_url}?next={path}')

        response = self.get_response(request)
        return response


def _log_failed_access(request, user=None):
    """Log unauthorized access attempts."""
    try:
        ip = _get_client_ip(request)
        AdminActivityLog.objects.create(
            admin=user,
            action='login_failed',
            details=f'Unauthorized access attempt to {request.path}',
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
    except Exception:
        pass  # Never let logging break the request cycle


def _get_client_ip(request):
    """Extract real client IP from request headers."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
