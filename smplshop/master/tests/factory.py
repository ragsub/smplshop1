from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker

from smplshop.master.models import Product, Store

fake = Faker()
Faker.seed(23)


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
