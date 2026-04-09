import os
import django
import sys
import traceback

# setup django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InkVeda.settings')
django.setup()

from django.conf import settings
from artworks.models import CustomOrder
from artworks.utils import send_custom_order_status_email

print("--- InkVeda Real-Data Email Test ---")

# Try to get the last order from the DB
order = CustomOrder.objects.last()

if not order:
    print("❌ No custom orders found in database. Please create one in Admin first.")
    sys.exit(1)

print(f"Testing with REAL Order ID: {order.id}")
print(f"Customer Name: {order.name}")
print(f"Status in DB: {order.status}")
print(f"Price in DB: {order.final_price}")

if order.status != 'Accepted':
    print("⚠️ Warning: Order is not 'Accepted'. Changing status temporarily for test...")
    order.status = 'Accepted'

print("\nSending email...")
try:
    send_custom_order_status_email(order)
    print("✅ Email sent based on REAL database values!")
    print(f"Recipient: {order.email}")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Site URL: {settings.SITE_URL}")
except Exception as e:
    print("❌ Email sending FAILED")
    traceback.print_exc()

print("\n--- Test End ---")
