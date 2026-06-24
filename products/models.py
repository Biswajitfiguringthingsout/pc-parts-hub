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

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to='products/',
        blank=True
    )

    def __str__(self):
        return self.name
class Build(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class BuildItem(models.Model):
    build = models.ForeignKey(
        Build,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.build.name} - {self.product.name}"
           