from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Manually redirecting to the hidden portal name
            return redirect('admin_portal')
        
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access Denied: You must be an administrator to view this page.")
    return wrapper_func
