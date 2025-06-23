from django.db import models

class Product(models.Model):
    TYPES = [
        ('Футболка', 'Футболка'), 
        ('Рубашка', 'Рубашка'), 
        ('Брюки', 'Брюки'),
        ('Джинсы', 'Джинсы'), 
        ('Платье', 'Платье'), 
        ('Костюм', 'Костюм'),
        ('Юбка', 'Юбка'),
        ('Свитер', 'Свитер'),
        ('Свитшот', 'Свитшот'),
        ('Худи', 'Худи'),
        ('Лонгслив', 'Лонгслив'),
        ('Шорты', 'Шорты'),
        ('Бермуды', 'Бермуды'),
        ('Куртка', 'Куртка'),
        ('Шапка', 'Шапка'),
        ('Кепка', 'Кепка'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=20, choices=TYPES)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name

    def available_sizes(self):
        return self.sizes.filter(quantity__gt=0)

    def is_fully_out_of_stock(self):
        # Check if any size has stock
        return not self.sizes.filter(quantity__gt=0).exists()

    def has_sizes(self):
        """Check if the product uses sizes"""
        return True  # All products now use sizes, even if it's just "Без Размера"

    def get_available_quantity(self):
        """Get available quantity for the product"""
        return sum(size.quantity for size in self.sizes.all())


class ProductSize(models.Model):
    SIZES = [
        ('S', 'S'), 
        ('M', 'M'), 
        ('L', 'L'), 
        ('XL', 'XL'), 
        ('XXL', 'XXL'),
        ('Без Размера', 'Без Размера')
    ]
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size = models.CharField(max_length=15, choices=SIZES)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size}"


class Message(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    phone = models.CharField(max_length=12)
    email = models.EmailField()
    text = models.TextField()

    def __str__(self):
        return f"Сообщение от {self.name}"
    


class Order(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    time_slot = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    preferred_messenger = models.CharField(max_length=20, blank=True, null=True,  default='neutral')


    def __str__(self):
        return f"Заказ от {self.name} в {self.time_slot}"
    
    @property
    def total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=15, blank=True, null=True)  # Increased max_length for "Без Размера"
    quantity = models.PositiveIntegerField(default=1)


class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
