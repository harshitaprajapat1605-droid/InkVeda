from django.core.management.base import BaseCommand
from django.conf import settings
from artworks.utils import send_resend_email

class Command(BaseCommand):
    help = 'Test Resend email configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Resend email test...'))
        
        to_email = settings.ARTIST_EMAIL
        subject = 'InkVeda - Resend Configuration Test'
        html_content = '<h1>Test Successful!</h1><p>This is a test email from your InkVeda project using Resend.</p>'
        
        if not settings.RESEND_API_KEY:
            self.stdout.write(self.style.ERROR('RESEND_API_KEY is missing from settings.'))
            return

        success = send_resend_email(to_email, subject, html_content)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {to_email}'))
        else:
            self.stdout.write(self.style.ERROR('Failed to send test email. Check console logs for errors.'))
