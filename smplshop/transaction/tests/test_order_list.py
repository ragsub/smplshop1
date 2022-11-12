from django.test import Client, TestCase
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.models import Store
from smplshop.master.tests.factory import StoreFactory
from smplshop.shop.tests.factory import OrderFactory
from smplshop.users.tests.factories import UserFactory


class TestOrderViewAndURL(TestCase):
    def test_url_to_name(self):
        resolver = resolve("/transaction/orders/")
        self.assertEqual(resolver.view_name, "smplshop.transaction:orders")

    def test_name_to_url(self):
        url = reverse("smplshop.transaction:orders")
        self.assertEqual(url, "/transaction/orders/")


class TestOrdersTemplateAndLogin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake.unique.clear()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    def test_status_code_on_login(self):
        response = self.client.get("/transaction/orders/")
        self.assertEqual(200, response.status_code)

    def test_status_code_without_login(self):
        self.client.logout()
        response = self.client.get("/transaction/orders/")
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/accounts/login/?next=/transaction/orders/")

    def test_correct_template(self):
        self.client.get("/transaction/orders/")
        self.assertTemplateUsed("transaction/orders.html")


class TestQueryset(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake.unique.clear()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self) -> None:
        super().setUp()
        fake.unique.clear()
        self.client.login(username=self.user.username, password=self.password)
        store1 = StoreFactory.create()
        store2 = StoreFactory.create()
        store3 = StoreFactory.create()
        OrderFactory.create_batch(20, store=store1)
        OrderFactory.create_batch(5, store=store2)
        OrderFactory.create_batch(10, store=store3)

    def test_queryset(self):
        response = self.client.get("/transaction/orders/")
        self.assertQuerysetEqual(Store.objects.all(), response.context["object_list"])
