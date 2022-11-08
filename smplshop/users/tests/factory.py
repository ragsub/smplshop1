from collections.abc import Sequence
from typing import Any

from django.conf import settings
from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory

from smplshop.functional_test.faker import fake


class UserFactory(DjangoModelFactory):
    username = LazyAttribute(lambda _: fake.user_name())
    name = LazyAttribute(lambda _: fake.name())
    email = LazyAttribute(lambda _: fake.email())

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ("username", "email")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = extracted if extracted else fake.password()
        self.set_password(password)  # type: ignore
