from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_emails(order):
    try:
        context = {
            'order': order,
            'site_url': settings.SITE_URL,
        }
        
        # Email to Customer
        html_content_customer = render_to_string('emails/order_success_customer.html', context)
        text_content_customer = strip_tags(html_content_customer)
        
        email_customer = EmailMultiAlternatives(
            subject=f"Order Received - InkVeda ({order.order_id})",
            body=text_content_customer,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email]
        )
        email_customer.attach_alternative(html_content_customer, "text/html")
        email_customer.send()

        # Email to Artist (Tanvi)
        html_content_artist = render_to_string('emails/order_success_admin.html', context)
        text_content_artist = strip_tags(html_content_artist)
        
        email_artist = EmailMultiAlternatives(
            subject=f"New Order Received - InkVeda ({order.order_id})",
            body=text_content_artist,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[getattr(settings, 'ARTIST_EMAIL', 'prajapattanvi5@gmail.com')]
        )
        email_artist.attach_alternative(html_content_artist, "text/html")
        email_artist.send()
        
    except Exception as e:
        print(f"Email error in send_order_emails: {e}")

def send_custom_order_submission_emails(order):
    try:
        context = {
            'order': order,
            'site_url': settings.SITE_URL,
        }
        
        # Email to Customer
        html_content_customer = render_to_string('emails/custom_order_received.html', context)
        text_content_customer = strip_tags(html_content_customer)
        email_customer = EmailMultiAlternatives(
            subject="Custom Order Received - InkVeda",
            body=text_content_customer,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email]
        )
        email_customer.attach_alternative(html_content_customer, "text/html")
        email_customer.send()

        # Email to Admin
        html_content_admin = render_to_string('emails/admin_custom_order_notification.html', context)
        text_content_admin = strip_tags(html_content_admin)
        
        # Manually ensure the reference image link is crystal clear in the subject or body if needed
        subject_admin = "New Custom Order Request - InkVeda"
        if order.reference_image:
             subject_admin += " (With Reference Image)"

        email_admin = EmailMultiAlternatives(
            subject=subject_admin,
            body=text_content_admin,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[getattr(settings, 'ARTIST_EMAIL', 'prajapattanvi5@gmail.com')]
        )
        email_admin.attach_alternative(html_content_admin, "text/html")
        email_admin.send()
        
    except Exception as e:
        print(f"Custom Order Email Error: {e}")

def generate_upi_link(amount):
    """Generates a UPI payment link with the specified amount."""
    pa = "7089089435@ybl"
    pn = "Tanvi Prajapat"
    return f"upi://pay?pa={pa}&pn={pn.replace(' ', '%20')}&am={amount}&cu=INR"

def send_custom_order_status_email(order):
    try:
        context = {
            'order': order,
            'site_url': settings.SITE_URL,
        }
        
        # Comprehensive mapping of status to details
        status_configs = {
            'Accepted': {
                'subject': "Your Custom Order is Accepted - InkVeda",
                'template': 'emails/custom_order_accepted.html'
            },
            'In Progress': {
                'subject': "Artistic Creation in Progress! - InkVeda",
                'template': 'emails/custom_order_in_progress.html'
            },
            'Completed': {
                'subject': "Your Masterpiece is Complete! - InkVeda",
                'template': 'emails/custom_order_completed.html'
            },
            'Rejected': {
                'subject': "Update on Your Custom Order Request - InkVeda",
                'template': 'emails/custom_order_rejected.html'
            },
        }
        
        config = status_configs.get(order.status)
        if not config:
            return

        if order.status == 'Accepted' and order.final_price:
            context['payment_link'] = generate_upi_link(order.final_price)

        html_content = render_to_string(config['template'], context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=config['subject'],
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
    except Exception as e:
        print(f"Custom Order Status Email Error: {e}")
