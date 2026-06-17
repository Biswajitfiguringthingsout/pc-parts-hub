from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY_CHOICES = [
    ('cpu', 'CPU'),
    ('gpu', 'GPU'),
    ('motherboard', 'Motherboard'),
    ('ram', 'RAM'),
    ('storage', 'Storage'),
    ('psu', 'PSU'),
    ('case', 'Case'),
    ('cooler', 'Cooler'),
    ('monitor', 'Monitor'),
    ('keyboard', 'Keyboard'),
    ('mouse', 'Mouse'),
    ('headset', 'Headset'),
]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return self.name
