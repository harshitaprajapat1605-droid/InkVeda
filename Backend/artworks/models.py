import uuid
import datetime
import random
import string
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

class Artwork(models.Model):
    CATEGORY_CHOICES = [
        ('Mandala', 'Mandala'),
        ('Zentangle', 'Zentangle'),
        ('Doodle', 'Doodle'),
        ('Typography', 'Typography'),
        ('Craft', 'Craft'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = CloudinaryField('image', folder='inkveda/artworks/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Razorpay', 'Razorpay'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending Verification'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
    ]
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # New Payment Fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_screenshot = CloudinaryField('payment_screenshot', folder='inkveda/payments/', blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_order_id()
        if not self.total_price:
            self.total_price = self.artwork.price * self.quantity
        super().save(*args, **kwargs)

    def generate_unique_order_id(self):
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            new_id = f"INKVEDA-{suffix}"
            if not Order.objects.filter(order_id=new_id).exists():
                return new_id

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"

class CustomOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted (Awaiting Payment)'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]
    SIZE_CHOICES = [
        ('A5', 'A5 (Small)'),
        ('A4', 'A4 (Medium)'),
        ('A3', 'A3 (Large)'),
    ]
    DETAIL_CHOICES = [
        ('Simple', 'Simple (Minimal Details)'),
        ('Medium', 'Medium (Standard Inkwork)'),
        ('Detailed', 'Detailed (Intricate Mandala/Zentangle)'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    art_type = models.CharField(max_length=50, choices=Artwork.CATEGORY_CHOICES, default='Mandala')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='A4')
    detail_level = models.CharField(max_length=20, choices=DETAIL_CHOICES, default='Simple')
    color_preference = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference_image = CloudinaryField('reference_image', folder='inkveda/custom_orders/', blank=True, null=True)
    deadline = models.DateField()
    
    # Pricing
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_price_confirmed = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_status = self.status
        self._initial_price = self.final_price

    def save(self, *args, **kwargs):
        # Automated pricing logic
        base = 300
        size_map = {'A5': 0, 'A4': 300, 'A3': 800}
        detail_map = {'Simple': 0, 'Medium': 300, 'Detailed': 700}
        calc_price = base + size_map.get(self.size, 0) + detail_map.get(self.detail_level, 0)

        if not self.estimated_price:
            self.estimated_price = calc_price
        
        # Automatically set final_price to the calculated estimate if not manually set
        if not self.final_price:
            self.final_price = calc_price

        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if not is_new:
            status_changed = self.status != self._initial_status
            price_newly_set = self._initial_price is None and self.final_price is not None
            
            if status_changed or price_newly_set:
                from .utils import send_custom_order_status_email
                send_custom_order_status_email(self)
                self._initial_status = self.status
                self._initial_price = self.final_price

    def __str__(self):
        return f"Custom Order from {self.name} ({self.status})"

    @property
    def tracking_id(self):
        return f"CUSTOM-{self.id}"
