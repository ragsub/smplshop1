from django.test import TestCase
from django.test.client import Client
from faker import Faker

from smplshop.master.tests.factory import StoreFactory
from smplshop.users.tests.factory import UserFactory


class TestShopMiddleware(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        Faker.seed(23)
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)
        self.shop = StoreFactory()

    def test_shop_is_returned(self):
        response = self.client.get("/shop/" + str(self.shop.code) + "/")
        self.assertEqual(response.request.shop, self.shop)
