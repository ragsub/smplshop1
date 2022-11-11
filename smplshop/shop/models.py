import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from smplshop.master.models import Product, ProductInStore, Store


class Cart(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        to=Store, on_delete=models.CASCADE, verbose_name="Store Name"
    )

    def __str__(self):
        return str(self.uuid) + "-" + str(self.store)

    @property
    def total_cart_price(self):
        return "%s" % (sum([float(obj.total_price) for obj in self.cartitem_set.all()]))  # type: ignore


class CartItem(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE, verbose_name="Cart For")
    product_in_store = models.ForeignKey(
        to=ProductInStore,
        on_delete=models.CASCADE,
        verbose_name="Product In Store",
        related_name="cart_items",
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(0.0)],
        verbose_name="Quanity",
        default=0,
    )

    class Meta:
        UniqueConstraint(
            fields=["cart", "product_in_store"], name="unique_cart_product"
        )

    def __str__(self):
        return str(self.cart) + "-" + str(self.product_in_store)

    @property
    def total_price(self):
        return "%s" % (self.product_in_store.price * self.quantity)  # type: ignore


class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("placed", "Order Placed"),
        ("accepted", "Order Accepted"),
        ("shipped", "Order Shipped"),
        ("delivered", "Order Delivered"),
        ("closed", "Order Closed"),
        ("cancelled", "Order Cancelled"),
    ]
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=ORDER_STATUS_CHOICES, default="placed"
    )

    def can_shop_cancel_order(self):
        return True if self.status in ["placed", "accepted", "shipped"] else False

    def cancel_order(self):
        if self.can_shop_cancel_order():
            self.status = "cancelled"
        else:
            raise ValidationError(
                _("{}{}{}".format("Order ", self.uuid, " cannot be cancelled"))
            )
        self.save()

    def can_shop_ship_order(self):
        return True if self.status == "accepted" else False

    def ship_order(self):
        if self.can_shop_ship_order():
            self.status = "shipped"
        else:
            raise ValidationError(
                _("{}{}{}".format("Order ", self.uuid, " cannot be shipped"))
            )
        self.save()

    def can_shop_accept_order(self):
        return True if self.status == "placed" else False

    def accept_order(self):
        if self.can_shop_accept_order():
            self.status = "accepted"
        else:
            raise ValidationError(
                _("{}{}{}".format("Order ", self.uuid, " cannot be accepted"))
            )
        self.save()

    def can_shop_deliver_order(self):
        return True if self.status == "shipped" else False

    def deliver_order(self):
        if self.can_shop_deliver_order():
            self.status = "delivered"
        else:
            raise ValidationError(
                _("{}{}{}".format("Order ", self.uuid, " cannot be delivered"))
            )
        self.save()

    def can_shop_close_order(self):
        return True if self.status == "delivered" else False

    def close_order(self):
        if self.can_shop_close_order():
            self.status = "closed"
        else:
            raise ValidationError(
                _("{}{}{}".format("Order ", self.uuid, " cannot be closed"))
            )
        self.save()

    @property
    def total_order_price(self):
        return "%s" % (sum([float(obj.total_price) for obj in self.orderitem_set.all()]))  # type: ignore


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.PROTECT)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    quantity = models.IntegerField(validators=[MinValueValidator(0)])

    @property
    def total_price(self):
        return self.price * self.quantity  # type: ignore
