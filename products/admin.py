from django.contrib import admin
from .models import Brand, Build, BuildItem, Product, Benchmark

admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Build)
admin.site.register(BuildItem)
admin.site.register(Benchmark)