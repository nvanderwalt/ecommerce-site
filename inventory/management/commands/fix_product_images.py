from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import Product
import cloudinary
import cloudinary.uploader
from pathlib import Path

class Command(BaseCommand):
    help = 'Fix product images by manually mapping them to image files'

    def handle(self, *args, **options):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        # Manual mapping of product names to image files
        product_image_mapping = {
            '6 Kg Medicine Ball': 'kettle_ball_set.jpeg',
            'Foam Roller': 'band_set.jpg',  # Using band image as placeholder
            'Jump Rope': 'band_set.jpg',    # Using band image as placeholder
            'Pull-Up Bar': 'pull_bar.webp',
            'Stationary Bike': 'station_bike.jpeg',
            'Resistance Bands': 'band_set.jpg',
            'Yoga Mat': 'yoga_mat.webp',
            '2 Kg Kettlebell': 'kettle_ball_set.jpeg',
            'Treadmill': 'tread.jpg',
        }

        product_images_dir = Path(settings.BASE_DIR) / 'product_images'
        
        for product_name, image_filename in product_image_mapping.items():
            try:
                product = Product.objects.get(name=product_name)
                image_path = product_images_dir / image_filename
                
                if image_path.exists():
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        str(image_path),
                        public_id=f"fitfusion/{product.name.lower().replace(' ', '_')}",
                        overwrite=True
                    )
                    
                    # Update the product with the Cloudinary URL
                    product.image = result['secure_url']
                    product.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully uploaded {image_filename} for {product.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Image file {image_filename} not found for {product.name}'
                        )
                    )
                    
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Product "{product_name}" not found')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to upload {image_filename} for {product_name}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('Product image fix completed!')
        )
