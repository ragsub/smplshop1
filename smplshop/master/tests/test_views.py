from random import randint

from django.conf import settings
from django.contrib.messages import get_messages
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


class TestStoreCreateView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)
        StoreFactory.create_batch(size=50)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/store/add/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/store/add/")
        self.assertEqual(resolver.view_name, "smplshop.master:store_add")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:store_add")
        self.assertEqual(url, "/master/store/add/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/store/add/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/store/add/")
        self.assertTemplateUsed(response=response, template_name="master/add.html")

    # check if record can be added
    def test_add_record(self):
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna"}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response, (reverse("smplshop.master:store_list") + "?new_code=krishna")
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Krishna Stores store added successfully")

    # check if duplicate record of code is rejeced
    def test_duplicate_code_record(self):
        Store.objects.create(name="Krishna Stores", code="krishna")
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna1 Stores", "code": "krishna"}
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("master/add.html")
        self.assertContains(response, "Store with this Store Code already exists.")

    # check if duplicate record of name is rejected
    def test_duplicate_name_record(self):
        Store.objects.create(name="Krishna Stores", code="krishna")
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna1"}
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("master/add.html")
        self.assertContains(response, "Store with this Store Name already exists.")

    # check if duplicate record of code and name is rejected
    def test_duplicate_code_and_name_record(self):
        Store.objects.create(name="Krishna Stores", code="krishna")
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna"}
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("master/add.html")
        self.assertContains(response, "Store with this Store Name already exists.")
        self.assertContains(response, "Store with this Store Code already exists.")

    # check if code accepts only characters and numbers. no spaces or special characters
    def test_only_alphanumeric_and_underscore(self):
        # cannot contain space
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna store"}
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("master/add.html")
        self.assertContains(
            response, "Store code can only be alphanumeric or underscore"
        )

        # cannot contain hyphen
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna-store"}
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("master/add.html")
        self.assertContains(
            response, "Store code can only be alphanumeric or underscore"
        )

        # can contain underscore and numbers
        response = self.client.post(
            "/master/store/add/", {"name": "Krishna Stores", "code": "krishna_store1"}
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            (reverse("smplshop.master:store_list") + "?new_code=krishna_store1"),
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Krishna Stores store added successfully")
