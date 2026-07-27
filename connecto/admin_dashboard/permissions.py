"""
Permission decorators and role helpers for the CONNECTO Admin Dashboard.
Uses Django's built-in auth system (separate from InstaUser).
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def get_admin_role(user):
    """Get the admin role for a Django auth user, or None."""
    if not user or not user.is_authenticated:
        return None
    try:
        return user.admin_profile.role
    except Exception:
        return None


def admin_required(view_func=None, role=None, redirect_url='admin_dashboard:login'):
    """
    Decorator that ensures the user is authenticated as a Django staff/superuser
    with optional role-based access control.

    Usage:
        @admin_required
        def my_view(request): ...

        @admin_required(role='super_admin')
        def super_only_view(request): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access the admin dashboard.')
                return redirect(redirect_url)

            if not (request.user.is_staff or request.user.is_superuser):
                messages.error(request, 'You do not have permission to access this area.')
                return redirect(redirect_url)

            if role:
                admin_role = get_admin_role(request.user)
                allowed_roles = _get_allowed_roles(role)
                if admin_role not in allowed_roles and not request.user.is_superuser:
                    messages.error(request, 'Insufficient permissions for this action.')
                    return redirect('admin_dashboard:dashboard')

            return func(request, *args, **kwargs)
        return wrapper

    if view_func is not None:
        # Called as @admin_required (no args)
        return decorator(view_func)
    # Called as @admin_required() or @admin_required(role='...')
    return decorator


def _get_allowed_roles(role):
    """Expand role shorthand to list of allowed roles (hierarchy)."""
    hierarchy = {
        'super_admin': ['super_admin'],
        'admin': ['super_admin', 'admin'],
        'moderator': ['super_admin', 'admin', 'moderator'],
        'content_moderator': ['super_admin', 'admin', 'moderator', 'content_moderator'],
        'support_staff': ['super_admin', 'admin', 'moderator', 'support_staff'],
        'viewer': ['super_admin', 'admin', 'moderator', 'content_moderator', 'support_staff', 'viewer'],
    }
    return hierarchy.get(role, [role])


# ─── Convenience permission checks ────────────────────────────────────────────

def can_manage_users(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin', 'moderator')


def can_delete_content(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin', 'content_moderator', 'moderator')


def can_ban_users(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin')


def can_manage_settings(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin')


def can_send_notifications(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin', 'moderator')


def can_approve_verification(user):
    role = get_admin_role(user)
    return user.is_superuser or role in ('super_admin', 'admin')


def can_view_analytics(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def get_permissions_context(user):
    """Return a dict of permissions for use in templates."""
    return {
        'perm_manage_users': can_manage_users(user),
        'perm_delete_content': can_delete_content(user),
        'perm_ban_users': can_ban_users(user),
        'perm_manage_settings': can_manage_settings(user),
        'perm_send_notifications': can_send_notifications(user),
        'perm_approve_verification': can_approve_verification(user),
        'perm_view_analytics': can_view_analytics(user),
        'admin_role': get_admin_role(user) or ('super_admin' if user.is_superuser else 'staff'),
    }
