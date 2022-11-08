from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from smplshop.functional_test.faker import fake
from smplshop.master.tests.factory import (
    ProductFactory,
    ProductInStoreFactory,
    StoreFactory,
)
from smplshop.shop.models import Cart, CartItem, Order, OrderItem
from smplshop.users.tests.factory import UserFactory


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    store = SubFactory(StoreFactory)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = SubFactory(CartFactory)
    product_in_store = SubFactory(ProductInStoreFactory)
    quantity = LazyAttribute(lambda _: fake.unique.random_int())


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = SubFactory(UserFactory)
    store = SubFactory(StoreFactory)


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    price = LazyAttribute(lambda _: fake.numerify("%##.##"))
    quantity = LazyAttribute(lambda _: fake.unique.random_int())
