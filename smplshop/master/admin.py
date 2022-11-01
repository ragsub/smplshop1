# Register your models here.
from django.contrib import admin

from .models import Product, ProductInStore, Store

admin.site.register(Store)
admin.site.register(Product)
admin.site.register(ProductInStore)
