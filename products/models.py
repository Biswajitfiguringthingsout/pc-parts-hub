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

    # Compatibility fields
    socket = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    memory_type = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    pcie_generation = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # Power fields
    power_draw = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Power consumption in Watts"
    )

    recommended_psu = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Recommended PSU Wattage"
    )

    # Capacity / Specs
    capacity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: 32GB, 2TB"
    )

    supported_cpu_sockets = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Comma separated. Example: AM4,AM5,LGA1700"
    )

    def __str__(self):
        return self.name 

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
    
