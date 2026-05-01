from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from artworks.models import Order, CustomOrder

def admin_portal_login(request):
    """Hidden portal for admin login only."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access restricted to staff only.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'is_admin_portal': True})

@login_required
def dashboard(request):
    # This remains as a legacy feature or can be disabled
    purchased_artworks = Order.objects.filter(user=request.user).order_by('-created_at')
    custom_orders = CustomOrder.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'purchased_artworks': purchased_artworks,
        'custom_orders': custom_orders,
    }
    return render(request, 'accounts/dashboard.html', context)

from .decorators import admin_only

@login_required
@admin_only
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')
