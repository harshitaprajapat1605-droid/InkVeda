from django.core.management.base import BaseCommand
import os
import cloudinary.uploader
from django.conf import settings
from artworks.models import Artwork, Order

class Command(BaseCommand):
    help = 'Migrates existing local images to Cloudinary'

    def handle(self, *args, **options):
        self.migrate_artworks()
        self.migrate_orders()
        self.stdout.write(self.style.SUCCESS('\nMigration process completed!'))

    def find_local_file(self, base_path):
        """Tries to find the local file, checking for common extensions if missing."""
        if os.path.exists(base_path):
            return base_path
        
        # Extensions to try
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG']
        for ext in extensions:
            test_path = base_path + ext
            if os.path.exists(test_path):
                return test_path
        return None

    def get_safe_str(self, field):
        """Safely convert a CloudinaryField to string, avoiding TypeError."""
        try:
            if not field:
                return None
            val = str(field)
            return val if val != 'None' else None
        except Exception:
            return None

    def migrate_artworks(self):
        self.stdout.write("Migrating Artworks...")
        artworks = Artwork.objects.all()
        for art in artworks:
            field_val = self.get_safe_str(art.image)
            
            if field_val and not field_val.startswith('http') and not field_val.startswith('inkveda/'):
                base_path = os.path.join(settings.MEDIA_ROOT, field_val)
                local_path = self.find_local_file(base_path)
                
                if local_path:
                    self.stdout.write(f"Uploading {local_path} to Cloudinary...")
                    try:
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="inkveda/artworks/"
                        )
                        art.image = result['public_id']
                        art.save()
                        self.stdout.write(self.style.SUCCESS(f"Successfully migrated {art.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to migrate {art.title}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"File not found locally (even with extensions): {base_path}"))
            else:
                self.stdout.write(f"Skipping {art.title} (already migrated or no image)")

    def migrate_orders(self):
        self.stdout.write("\nMigrating Orders...")
        orders = Order.objects.all()
        for order in orders:
            field_val = self.get_safe_str(order.payment_screenshot)
            
            if field_val and not field_val.startswith('http') and not field_val.startswith('inkveda/'):
                base_path = os.path.join(settings.MEDIA_ROOT, field_val)
                local_path = self.find_local_file(base_path)
                
                if local_path:
                    self.stdout.write(f"Uploading screenshot for order {order.order_id}...")
                    try:
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="inkveda/payments/"
                        )
                        order.payment_screenshot = result['public_id']
                        order.save()
                        self.stdout.write(self.style.SUCCESS(f"Successfully migrated screenshot for {order.order_id}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to migrate screenshot for {order.order_id}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Screenshot not found locally: {base_path}"))
            else:
                self.stdout.write(f"Skipping Order {order.order_id} (no screenshot or already migrated)")
