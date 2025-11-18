from functools import wraps
from django.http import HttpResponseForbidden
from .models import StaffRole

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            try:
                staff = StaffRole.objects.get(user=request.user)
            except StaffRole.DoesNotExist:
                return HttpResponseForbidden("Access denied")

            if staff.role in allowed_roles:
                return view_func(self, request, *args, **kwargs)

            return HttpResponseForbidden("Access denied for your role")

        return wrapper
    return decorator

def _find_request_arg(args, kwargs):
    # find the DRF request instance in args or kwargs
    for a in args:
        # DRF Request has attributes: user & method & data
        if hasattr(a, "user") and hasattr(a, "method"):
            return a
    if 'request' in kwargs:
        return kwargs['request']
    return None
