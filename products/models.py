from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('monitor', 'Monitor'),
        ('headset', 'Headset'),
    ]

   
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
