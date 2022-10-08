from random import randint

from django.conf import settings
from django.core.paginator import Paginator
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse
from faker import Faker

from smplshop.master.models import Store
from smplshop.users.tests.factory import UserFactory

from .factory import StoreFactory

fake = Faker()
Faker.seed(23)


class StoreListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

        cls.fields = ["code", "name"]
        StoreFactory.create_batch(size=50)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/store/")
        self.assertEqual(resolver.view_name, "smplshop.master:store_list")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:store_list")
        self.assertEqual(url, "/master/store/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/store/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/store/")
        self.assertTemplateUsed(
            response=response, template_name="master/store_list.html"
        )

    # check if all records are shown
    def test_pagination(self):

        all_stores = Store.objects.all().values_list(*self.fields)
        pages = Paginator(all_stores, settings.ITEMS_PER_PAGE)

        response = self.client.get("/master/store/")
        page_1 = pages.page(1)
        self.assertQuerysetEqual(page_1.object_list, response.context["object_list"])

        page_last = pages.page(pages.num_pages)
        response = self.client.get("/master/store/?page=" + str(pages.num_pages))
        self.assertQuerysetEqual(page_last.object_list, response.context["object_list"])

        page_n = pages.page(randint(1, pages.num_pages))
        response = self.client.get("/master/store/?page=" + str(page_n.number))
        self.assertQuerysetEqual(page_n.object_list, response.context["object_list"])

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/store/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    # check if record can be added

    # check if duplicate record of code is rejeced
    # check if duplicate record of name is rejected
    # check if code accepts only characters and numbers. no spaces or special characters
