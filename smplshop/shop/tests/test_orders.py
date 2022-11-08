from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.tests.factory import StoreFactory
from smplshop.shop.models import Order
from smplshop.users.tests.factory import UserFactory

from .factory import OrderFactory


class TestCustomerOrder(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self):
        super().setUp()
        fake.unique.clear()
        self.client.login(username=self.user.username, password=self.password)
        self.store1 = StoreFactory.create()
        self.store2 = StoreFactory.create()
        self.store3 = StoreFactory.create()
        self.store1order1 = OrderFactory.create(store=self.store1, user=self.user)
        self.store1order2 = OrderFactory.create(store=self.store1, user=self.user)
        self.store2order1 = OrderFactory.create(store=self.store2, user=self.user)
        self.store2order2 = OrderFactory.create(store=self.store2, user=self.user)
        self.store2order3 = OrderFactory.create(store=self.store2, user=self.user)
        self.store2order4 = OrderFactory.create(store=self.store2, user=self.user)
        self.store3order1 = OrderFactory.create(store=self.store3, user=self.user)
        self.store3order2 = OrderFactory.create(store=self.store3, user=self.user)
        self.store3order3 = OrderFactory.create(store=self.store3, user=self.user)

    def test_orders_after_login(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/orders/")
        )
        self.assertEqual(response.status_code, 200)

    def test_orders_before_login(self):
        self.client.logout()
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/orders/")
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "{}{}{}".format(
                "/accounts/login/?next=/shop/", self.store1.code, "/orders/"
            ),
        )

    def test_url_resolves_to_view(self):
        resolver = resolve("{}{}{}".format("/shop/", self.store1.code, "/orders/"))
        self.assertEqual(resolver.view_name, "smplshop.shop:customer_orders")

    def test_view_resolves_to_url(self):
        url = reverse(
            "smplshop.shop:customer_orders", kwargs={"shop": self.store1.code}
        )
        self.assertEqual(url, "{}{}{}".format("/shop/", self.store1.code, "/orders/"))

    def test_template_used(self):
        self.client.get("{}{}{}".format("/shop/", self.store1.code, "/orders/"))
        self.assertTemplateUsed("shop/orders.html")

    def test_empty_queryset(self):
        self.client.logout()
        user = UserFactory.create(password=self.password)
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/orders/")
        )
        self.assertQuerysetEqual(response.context["object_list"], Order.objects.none())

    def test_queryset_for_store1(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/orders/")
        )
        self.assertQuerysetEqual(
            response.context["object_list"],
            Order.objects.filter(store=self.store1, user=self.user),
            ordered=False,
        )

    def test_queryset_for_store2(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store2.code, "/orders/")
        )
        self.assertQuerysetEqual(
            response.context["object_list"],
            Order.objects.filter(store=self.store2, user=self.user),
            ordered=False,
        )

    def test_queryset_for_store3(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store3.code, "/orders/")
        )
        self.assertQuerysetEqual(
            response.context["object_list"],
            Order.objects.filter(store=self.store3, user=self.user),
            ordered=False,
        )
