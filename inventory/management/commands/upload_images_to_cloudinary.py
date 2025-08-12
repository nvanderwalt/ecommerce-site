from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import Product
import os
import cloudinary
import cloudinary.uploader
from pathlib import Path

class Command(BaseCommand):
    help = 'Upload local product images to Cloudinary'

    def handle(self, *args, **options):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        # Get the product_images directory
        product_images_dir = Path(settings.BASE_DIR) / 'product_images'
        
        if not product_images_dir.exists():
            self.stdout.write(
                self.style.ERROR('Product images directory not found')
            )
            return

        # Get all products
        products = Product.objects.all()
        
        for product in products:
            # Try to find a matching image file
            image_found = False
            
            for image_file in product_images_dir.iterdir():
                if image_file.is_file():
                    # Check if the filename matches the product name (case insensitive)
                    product_name_lower = product.name.lower().replace(' ', '_').replace('-', '_')
                    file_name_lower = image_file.stem.lower().replace(' ', '_').replace('-', '_')
                    
                    if product_name_lower in file_name_lower or file_name_lower in product_name_lower:
                        try:
                            # Upload to Cloudinary
                            result = cloudinary.uploader.upload(
                                str(image_file),
                                public_id=f"fitfusion/{product.name.lower().replace(' ', '_')}",
                                overwrite=True
                            )
                            
                            # Update the product with the Cloudinary URL
                            product.image = result['secure_url']
                            product.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Successfully uploaded {image_file.name} for {product.name}'
                                )
                            )
                            image_found = True
                            break
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Failed to upload {image_file.name} for {product.name}: {str(e)}'
                                )
                            )
            
            if not image_found:
                self.stdout.write(
                    self.style.WARNING(
                        f'No matching image found for product: {product.name}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('Image upload process completed!')
        )
