from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from smplshop.functional_test.faker import fake
from smplshop.master.models import Product, ProductInStore, Store


class StoreFactory(DjangoModelFactory):
    class Meta:
        model = Store
        django_get_or_create = ("code", "name")

    code = LazyAttribute(lambda _: fake.unique.word())  # type: ignore
    name = LazyAttribute(lambda _: fake.unique.company())  # type: ignore


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("code", "name")

    code = LazyAttribute(lambda _: fake.unique.word())  # type: ignore
    name = LazyAttribute(lambda _: fake.unique.company())  # type: ignore


class ProductInStoreFactory(DjangoModelFactory):
    class Meta:
        model = ProductInStore
        django_get_or_create = ("store", "product")

    store = SubFactory(StoreFactory)
    product = SubFactory(ProductFactory)
    price = LazyAttribute(lambda _: fake.numerify("%##.##"))  # type: ignore
