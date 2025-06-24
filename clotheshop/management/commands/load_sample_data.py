from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from clotheshop.models import Product, ProductSize
import requests
import os

class Command(BaseCommand):
    help = 'Load sample products with images'

    def handle(self, *args, **options):
        # Проверяем, есть ли уже товары в базе
        if Product.objects.exists():
            self.stdout.write('Products already exist, skipping sample data loading.')
            return
            
        self.stdout.write('Loading sample products...')
        
        # Создаем тестовые продукты
        sample_products = [
            {
                'name': 'Футболка UNI',
                'price': 1500.00,
                'product_type': 'Футболка',
                'image_url': 'https://via.placeholder.com/400x500/FF6B6B/FFFFFF?text=UNI+Футболка',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Рубашка Классическая',
                'price': 2500.00,
                'product_type': 'Рубашка',
                'image_url': 'https://via.placeholder.com/400x500/4ECDC4/FFFFFF?text=Классическая+Рубашка',
                'sizes': ['M', 'L', 'XL', 'XXL']
            },
            {
                'name': 'Джинсы Универсальные',
                'price': 3500.00,
                'product_type': 'Джинсы',
                'image_url': 'https://via.placeholder.com/400x500/45B7D1/FFFFFF?text=Универсальные+Джинсы',
                'sizes': ['S', 'M', 'L', 'XL']
            }
        ]
        
        for product_data in sample_products:
            # Создаем продукт
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'price': product_data['price'],
                    'product_type': product_data['product_type'],
                }
            )
            
            if created or not product.image:
                # Загружаем изображение
                try:
                    response = requests.get(product_data['image_url'])
                    if response.status_code == 200:
                        img_temp = NamedTemporaryFile(delete=True)
                        img_temp.write(response.content)
                        img_temp.flush()
                        
                        # Сохраняем изображение
                        filename = f"{product_data['name'].replace(' ', '_').lower()}.jpg"
                        product.image.save(filename, File(img_temp), save=True)
                        self.stdout.write(f'Created product: {product.name} with image')
                    else:
                        self.stdout.write(f'Failed to download image for {product.name}')
                except Exception as e:
                    self.stdout.write(f'Error loading image for {product.name}: {e}')
            
            # Создаем размеры
            for size_name in product_data['sizes']:
                ProductSize.objects.get_or_create(
                    product=product,
                    size=size_name,
                    defaults={'quantity': 10}
                )
        
        self.stdout.write(self.style.SUCCESS('Sample products loaded successfully!')) 