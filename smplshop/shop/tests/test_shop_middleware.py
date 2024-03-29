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
        self.assertEqual(response.wsgi_request.shop, self.shop)
        self.assertEqual(200, response.status_code)

    def test_incorrect_shop_is_rejected(self):
        response = self.client.get("/shop/test/")
        self.assertEqual(404, response.status_code)
        self.assertContains(
            response=response, text="Shop test does not exist", status_code=404
        )
