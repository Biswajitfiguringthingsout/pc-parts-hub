from django.contrib import admin
from .models import Product
from .models import Brand
from .models import Build
from .models import BuildItem

admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Build)
admin.site.register(BuildItem)