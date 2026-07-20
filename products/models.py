from django.db import models
from django.contrib.auth.models import User

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
    form_factor = models.CharField(
    max_length=20,
    blank=True,
    null=True,
    help_text="ATX, Micro-ATX, Mini-ITX"
    )

    supported_form_factors = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="Example: ATX,Micro-ATX,Mini-ITX"
    )
    gpu_length = models.IntegerField(
    null=True,
    blank=True,
    help_text="Length in mm"
    )

    max_gpu_length = models.IntegerField(
    null=True,
    blank=True,
    help_text="Maximum supported GPU length"
    )
    cooler_height = models.IntegerField(
    null=True,
    blank=True
    )

    max_cooler_height = models.IntegerField(
    null=True,
    blank=True
    )
    storage_interface = models.CharField(
    max_length=20,
    blank=True,
    null=True,
    choices=[
        ("M.2", "M.2"),
        ("SATA", "SATA"),
    ]
    )
    m2_slots = models.IntegerField(
    null=True,
    blank=True,
    default=0
    )

    sata_ports = models.IntegerField(
    null=True,
    blank=True,
    default=0
    )
    # Performance

    gaming_score = models.PositiveIntegerField(
    default=0,
    help_text="0-100"
    )

    productivity_score = models.PositiveIntegerField(
    default=0
    )

    efficiency_score = models.PositiveIntegerField(
    default=0
    )

    release_year = models.PositiveIntegerField(
    blank=True,
    null=True
    )

    tier = models.CharField(
    max_length=20,
    blank=True,
    choices=[
        ("Entry","Entry"),
        ("Budget","Budget"),
        ("Mid Range","Mid Range"),
        ("High End","High End"),
        ("Flagship","Flagship"),
    ]
    )
    fps_1080p = models.PositiveIntegerField(
    blank=True,
    null=True
    )

    fps_1440p = models.PositiveIntegerField(
    blank=True,
    null=True
    )

    fps_4k = models.PositiveIntegerField(
    blank=True,
    null=True
    )
    learning_tip = models.TextField(
    blank=True
    )
    build_order = models.PositiveIntegerField(
    default=0
    )
    difficulty = models.CharField(
    max_length=20,
    blank=True,
    choices=[
        ("Easy","Easy"),
        ("Medium","Medium"),
        ("Hard","Hard")
    ]
    )

    def __str__(self):
        return self.name
BUILD_TYPES = [
    ("gaming", "Gaming"),
    ("streaming", "Streaming"),
    ("workstation", "Workstation"),
    ("editing", "Editing"),
    ("office", "Office"),
    ("ai", "AI / Machine Learning"),
    ("mini_itx", "Mini ITX"),
    ("server", "Server / NAS"),
    ("custom", "Custom"),
]
class Build(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="builds",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)

    description = models.CharField(
        max_length=200,
        blank=True,
    )

    build_type = models.CharField(
        max_length=20,
        choices=BUILD_TYPES,
        default="gaming",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

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
    
class Benchmark(models.Model):
    gpu = models.ForeignKey(Product, on_delete=models.CASCADE)
    game = models.CharField(max_length=100)
    resolution = models.CharField(max_length=20)
    fps = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.gpu.name} - {self.game} ({self.resolution})"