import uuid

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Store(models.Model):
    code = models.CharField(
        max_length=15,
        verbose_name="Store Code",
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9_]+$",
                _("Store code can only be alphanumeric or underscore"),
            )
        ],
    )
    name = models.CharField(
        max_length=40, verbose_name="Store Name", blank=False, unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("code", "name")


class Product(models.Model):
    code = models.CharField(
        max_length=25,
        verbose_name="Product Code",
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9_]+$",
                _("Product code can only be alphanumeric or underscore"),
            )
        ],
    )
    name = models.CharField(
        max_length=50, verbose_name="Store Name", blank=False, unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("code", "name")


class ProductInStore(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        Store, to_field="name", on_delete=models.CASCADE, verbose_name="Store"
    )
    product = models.ForeignKey(
        Product, to_field="name", on_delete=models.PROTECT, verbose_name="Product"
    )
    price = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name="Price")

    def __str__(self):
        return str(self.product) + " in " + str(self.store)

    class Meta:
        ordering = ("store", "product")
        constraints = [
            UniqueConstraint(
                fields=["store", "product"], name="unique_product_in_store"
            ),
        ]
        verbose_name = "Product In Store"
