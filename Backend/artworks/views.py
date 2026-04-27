import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Artwork, Order, CustomOrder
from .forms import ArtworkOrderForm, CustomOrderForm, UPIPaymentForm, ArtworkForm


from .utils import send_order_emails, send_custom_order_submission_emails, send_custom_order_status_email

def home(request):
    featured_artworks = Artwork.objects.filter(is_available=True)[:4]
    return render(request, 'artworks/home.html', {'featured_artworks': featured_artworks})

def gallery(request):
    category = request.GET.get('category')
    artworks_list = Artwork.objects.filter(is_available=True)
    if category:
        artworks_list = artworks_list.filter(category=category)
    
    paginator = Paginator(artworks_list, 8) # 8 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = [c[0] for c in Artwork.CATEGORY_CHOICES]
    return render(request, 'artworks/gallery.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category
    })

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    return render(request, 'artworks/artwork_detail.html', {'artwork': artwork})

def checkout(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    if request.method == 'POST':
        form = ArtworkOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.artwork = artwork
            order.payment_method = 'UPI'
            order.payment_status = 'Pending'
            order.save() # save() calculates total_price and order_id

            return redirect('upi_payment', order_id=order.order_id)
    else:
        form = ArtworkOrderForm(initial={'quantity': 1})
    return render(request, 'artworks/checkout.html', {'form': form, 'artwork': artwork})

def receipt(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'artworks/receipt.html', {'order': order})

def upi_payment(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == 'POST':
        form = UPIPaymentForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            # Send emails after payment details are submitted
            send_order_emails(order)
            return redirect('receipt', order_id=order.order_id)
    else:
        form = UPIPaymentForm(instance=order)
    
    context = {
        'order': order,
        'form': form,
        'upi_link': f"upi://pay?pa=7089089435@ybl&pn=Tanvi%20Prajapat&cu=INR&am={order.total_price}"
    }
    return render(request, 'artworks/upi_payment.html', context)

def track_order(request):
    order = None
    custom_order = None
    error_message = None
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '').strip()
        email = request.POST.get('email', '').strip()
        
        if order_id.startswith('CUSTOM-'):
            try:
                # Extract numeric ID
                numeric_id = order_id.replace('CUSTOM-', '')
                custom_order = CustomOrder.objects.get(id=numeric_id, email=email)
            except (CustomOrder.DoesNotExist, ValueError):
                error_message = "No custom order found with the provided details."
        else:
            try:
                order = Order.objects.get(order_id=order_id, email=email)
            except Order.DoesNotExist:
                error_message = "No order found with the provided details."
                
    return render(request, 'artworks/track_order.html', {
        'order': order, 
        'custom_order': custom_order,
        'error_message': error_message
    })

def custom_order(request):
    if request.method == 'POST':
        form = CustomOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            # Send initial notification emails
            send_custom_order_submission_emails(order)
            return render(request, 'artworks/custom_order_success.html')
    else:
        form = CustomOrderForm()
    return render(request, 'artworks/custom_order.html', {'form': form})

def custom_order_payment(request, pk):
    order = get_object_or_404(CustomOrder, pk=pk)
    if not order.final_price:
        return redirect('home') # Price not set yet
    
    from .utils import generate_upi_link
    payment_link = generate_upi_link(order.final_price)
    
    return render(request, 'artworks/custom_order_payment.html', {
        'order': order,
        'payment_link': payment_link
    })

def about(request):
    return render(request, 'artworks/about.html')

def contact(request):
    return render(request, 'artworks/contact.html')

from accounts.decorators import admin_only

@admin_only
def admin_analytics(request):
    total_orders = Order.objects.filter(payment_status='Paid').count()
    total_revenue = Order.objects.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_artworks = Artwork.objects.count()
    pending_orders = Order.objects.filter(status='Pending', payment_status='Paid').count()
    
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today, payment_status='Paid').count()
    
    month_start = today.replace(day=1)
    monthly_revenue = Order.objects.filter(created_at__date__gte=month_start, payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    recent_orders = Order.objects.filter(payment_status='Paid').order_by('-created_at')[:10]
    
    return render(request, 'artworks/admin_analytics.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_artworks': total_artworks,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
    })

@admin_only
def custom_order_dashboard(request):
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    orders = CustomOrder.objects.all().order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    if search_query:
        orders = orders.filter(models.Q(name__icontains=search_query) | models.Q(email__icontains=search_query))
    
    return render(request, 'artworks/dashboard/custom_orders.html', {
        'orders': orders,
        'status_choices': CustomOrder.STATUS_CHOICES,
        'current_status': status_filter
    })

@admin_only
def custom_order_admin_detail(request, pk):
    order = get_object_or_404(CustomOrder, pk=pk)
    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.final_price = request.POST.get('final_price') or None
        order.payment_status = request.POST.get('payment_status')
        order.save()
        return redirect('custom_order_dashboard')
    
    return render(request, 'artworks/dashboard/custom_order_detail.html', {'order': order})



@admin_only
def manage_artworks(request):
    artworks = Artwork.objects.all().order_by('-created_at')
    return render(request, 'artworks/dashboard/manage_artworks.html', {'artworks': artworks})

@admin_only
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.uploaded_by = request.user
            artwork.save()
            return redirect('manage_artworks')
    else:
        form = ArtworkForm()
    return render(request, 'artworks/dashboard/artwork_form.html', {'form': form, 'title': 'Add New Masterpiece'})

@admin_only
def edit_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            return redirect('manage_artworks')
    else:
        form = ArtworkForm(instance=artwork)
    return render(request, 'artworks/dashboard/artwork_form.html', {'form': form, 'title': 'Edit Masterpiece'})

@admin_only
def delete_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    if request.method == 'POST':
        artwork.delete()
        return redirect('manage_artworks')
    return render(request, 'artworks/dashboard/delete_confirm.html', {'item': artwork})
