import resend
from django.conf import settings
from django.template.loader import render_to_string

def send_resend_email(to_email, subject, html_content):
    """Reusable helper to send email via Resend API."""
    try:
        if not settings.RESEND_API_KEY:
            print("RESEND_API_KEY missing. Email skipped.")
            return False

        resend.api_key = settings.RESEND_API_KEY

        # If in DEBUG mode, redirect all emails to the artist email to avoid Resend's restrictions on unverified domains
        actual_recipient = to_email
        if settings.DEBUG:
            actual_recipient = settings.ARTIST_EMAIL
            subject = f"[TEST -> {to_email}] {subject}"

        response = resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [actual_recipient],
            "subject": subject,
            "html": html_content,
        })

        print(f"Resend email sent to {actual_recipient}:", response)
        return True

    except Exception as e:
        print(f"Resend email to {to_email} failed:", e)
        return False

def send_order_emails(order):
    context = {
        'order': order,
        'site_url': settings.SITE_URL,
    }

    # ---------------- CUSTOMER EMAIL ----------------
    try:
        html_content_customer = render_to_string('emails/order_success_customer.html', context)
        subject_customer = f"Order Received - InkVeda ({order.order_id})"
        send_resend_email(order.email, subject_customer, html_content_customer)
    except Exception as e:
        print("Customer order email process failed:", e)

    # ---------------- ADMIN EMAIL ----------------
    try:
        html_content_artist = render_to_string('emails/order_success_admin.html', context)
        subject_admin = f"New Order Received - InkVeda ({order.order_id})"
        send_resend_email(settings.ARTIST_EMAIL, subject_admin, html_content_artist)
    except Exception as e:
        print("Admin order email process failed:", e)


def send_custom_order_submission_emails(order):
    context = {
        'order': order,
        'site_url': settings.SITE_URL,
    }

    # ---------------- CUSTOMER EMAIL ----------------
    try:
        html_content_customer = render_to_string('emails/custom_order_received.html', context)
        subject_customer = "Custom Order Received - InkVeda"
        send_resend_email(order.email, subject_customer, html_content_customer)
    except Exception as e:
        print("Customer custom order email process failed:", e)

    # ---------------- ADMIN EMAIL ----------------
    try:
        html_content_admin = render_to_string('emails/admin_custom_order_notification.html', context)
        subject_admin = "New Custom Order Request - InkVeda"
        if order.reference_image:
            subject_admin += " (With Reference Image)"
        
        send_resend_email(settings.ARTIST_EMAIL, subject_admin, html_content_admin)
    except Exception as e:
        print("Admin custom order email process failed:", e)


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
        send_resend_email(order.email, config['subject'], html_content)

    except Exception as e:
        print("Custom order status email process failed:", e)

def send_purchase_order_status_email(order):
    try:
        context = {
            'order': order,
            'site_url': settings.SITE_URL,
        }

        subject = f"Update on your InkVeda Order - {order.order_id}"
        html_content = render_to_string('emails/purchase_order_status_update.html', context)
        
        send_resend_email(order.email, subject, html_content)

    except Exception as e:
        print("Purchase order status email process failed:", e)