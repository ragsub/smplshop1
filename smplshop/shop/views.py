import uuid as uid
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, FilteredRelation, Q
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from smplshop.master.models import ProductInStore, Store

from .models import Cart, CartItem, Order, OrderItem


# Create your views here.
class ShopFrontView(ListView):
    model: ModelBase = ProductInStore
    template_name: str = "shop/shop_front.html"

    def get_queryset(self) -> QuerySet[Any]:
        shop = self.kwargs["shop"]
        store = Store.objects.get(code=shop)

        qs = super().get_queryset().filter(store=store)

        if self.request.session.get(shop, None):
            cart_uuid = self.request.session.get(shop, None)
            cart = Cart.objects.get(uuid=cart_uuid)
            qs = (
                qs.prefetch_related("cart_items")
                .values("uuid", "store", "product", "price")
                .annotate(
                    item_in_cart=FilteredRelation(
                        "cart_items", condition=Q(cart_items__cart=cart)
                    )
                )
                .annotate(quantity=F("item_in_cart__quantity"))
            )

        return qs  # type: ignore


def add_to_cart(
    request: HttpRequest, shop: str, product_in_store_uuid: uid.UUID
) -> HttpResponse:

    product_in_store = get_object_or_404(
        ProductInStore, uuid=product_in_store_uuid, store__code=shop
    )
    if not request.session.get(shop, None):
        # if the cookie is not there,
        # create an empty cart and create the cookie
        # the empty cart will have user as None if
        # the user is not logged in
        store = Store.objects.get(code=shop)
        new_cart = Cart.objects.create(store=store)
        request.session[shop] = str(new_cart.uuid)
        request.session.save()

    cart_uuid = request.session.get(shop, None)
    cart = Cart.objects.get(uuid=cart_uuid)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product_in_store=product_in_store
    )

    cart_item.quantity = cart_item.quantity + 1
    cart_item.save()

    return redirect("smplshop.shop:shop_front", shop=shop)


class CartView(ListView):
    model: ModelBase = Cart
    template_name: str = "shop/cart.html"

    def get_store(self):
        shop = self.kwargs["shop"]
        store = Store.objects.get(code=shop)
        return shop, store

    def get_queryset(self) -> QuerySet[Any]:
        shop, store = self.get_store()
        qs = super().get_queryset().filter(store=store)

        if self.request.session.get(shop, None):
            cart_uuid = self.request.session.get(shop, None)
            get_object_or_404(Cart, uuid=cart_uuid, store=store)
            qs = qs.filter(uuid=cart_uuid)
            qs = (
                qs.prefetch_related("cartitem_set")
                .annotate(
                    #    store=F("cartitem__product_in_store__store"),
                    product=F("cartitem__product_in_store__product"),
                    price=F("cartitem__product_in_store__price"),
                    quantity=F("cartitem__quantity"),
                )
                .annotate(total_price=F("price") * F("quantity"))
            )
        else:
            qs = qs.none()

        return qs  # type: ignore

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop, store = self.get_store()
        if self.request.session.get(shop, None):
            cart_uuid = self.request.session.get(shop, None)
            context["total_cart_price"] = Cart.objects.get(
                store=store, uuid=cart_uuid
            ).total_cart_price
        else:
            context["total_cart_price"] = 0

        return context


@login_required
def place_order(request: HttpRequest, shop: str) -> HttpResponse:
    store = Store.objects.get(code=shop)
    if request.session.get(shop, None):
        cart_uuid = request.session.get(shop, None)
        cart = get_object_or_404(Cart, uuid=cart_uuid, store=store)
        if CartItem.objects.filter(cart=cart).exists():
            new_order = Order.objects.create(user=request.user, store=store)
            for item in CartItem.objects.filter(cart=cart):
                OrderItem.objects.create(
                    order=new_order,
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            cart.delete()
            del request.session[shop]
            request.session.modified = True
            messages.success(request, _("Order " + str(new_order.uuid) + " created"))
        else:
            messages.error(request, _("No items in cart to order"))
    else:
        messages.error(request, _("No items in cart to order"))

    return redirect("smplshop.shop:orders", shop=shop)


class OrderListView(LoginRequiredMixin, ListView):
    model: ModelBase = Order
    template_name: str = "shop/orders.html"

    def get_queryset(self) -> QuerySet[Any]:
        shop = self.kwargs["shop"]
        store = Store.objects.get(code=shop)

        qs = super().get_queryset().filter(Q(store=store) & Q(user=self.request.user))

        return qs
