from random import randint

from django.conf import settings
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from django.db.models import Value
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.models import Product
from smplshop.users.tests.factory import UserFactory

from .factory import ProductFactory


class ProductListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

        cls.fields = ["code", "name"]
        ProductFactory.create_batch(size=50)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/product/")
        self.assertEqual(resolver.view_name, "smplshop.master:product_list")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:product_list")
        self.assertEqual(url, "/master/product/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/product/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/product/")
        self.assertTemplateUsed(
            response=response, template_name="master/product_list.html"
        )

    # check if all records are shown
    def test_pagination(self):

        all_product = (
            Product.objects.all().values_list(*self.fields).annotate(new=Value(""))
        )
        pages = Paginator(all_product, settings.ITEMS_PER_PAGE)

        response = self.client.get("/master/product/")
        page_1 = pages.page(1)
        self.assertQuerysetEqual(page_1.object_list, response.context["object_list"])

        page_last = pages.page(pages.num_pages)
        response = self.client.get("/master/product/?page=" + str(pages.num_pages))
        self.assertQuerysetEqual(page_last.object_list, response.context["object_list"])

        page_n = pages.page(randint(1, pages.num_pages))
        response = self.client.get("/master/product/?page=" + str(page_n.number))
        self.assertQuerysetEqual(page_n.object_list, response.context["object_list"])

    # check if new records are identified
    def test_new_records(self):
        product = Product.objects.get(id=randint(1, 50))
        response = self.client.get("/master/product/?new_code=" + str(product.code))
        self.assertContains(response, product.code)
        self.assertContains(response, product.name)
        self.assertContains(response, "New")

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/product/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)


class TestProductCreateView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)
        ProductFactory.create_batch(size=50)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/product/add/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/product/add/")
        self.assertEqual(resolver.view_name, "smplshop.master:product_add")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:product_add")
        self.assertEqual(url, "/master/product/add/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/product/add/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/product/add/")
        self.assertTemplateUsed(response=response, template_name="genericview/add.html")

    # check if record can be added
    def test_add_record(self):
        response = self.client.post(
            "/master/product/add/", {"name": "tata tea 50gms", "code": "tata_tea_50gms"}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            (reverse("smplshop.master:product_list") + "?new_code=tata_tea_50gms"),
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "tata tea 50gms product added successfully")

    # check if duplicate record of code is rejeced
    def test_duplicate_code_record(self):
        Product.objects.create(name="Tata Tea 50gms", code="tata_tea_50gms")
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 100gms", "code": "tata_tea_50gms"},
        )
        self.assertContains(
            response,
            "tata_tea_50gms is already a product code",
            status_code=400,
        )

    # check if duplicate record of name is rejected
    def test_duplicate_name_record(self):
        Product.objects.create(name="Tata Tea 50gms", code="tata_tea_50gms")
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 50gms", "code": "tata_tea_100gms"},
        )
        self.assertContains(
            response, "Tata Tea 50gms is already a product name", status_code=400
        )

    # check if duplicate record of code and name is rejected
    def test_duplicate_code_and_name_record(self):
        Product.objects.create(name="Tata Tea 50gms", code="tata_tea_100gms")
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 50gms", "code": "tata_tea_100gms"},
        )
        self.assertTemplateUsed("genericview/add.html")
        self.assertContains(
            response, "Tata Tea 50gms is already a product name", status_code=400
        )
        self.assertContains(
            response, "tata_tea_100gms is already a product code", status_code=400
        )

    # check duplicates across cases are rejected
    def test_duplicate_across_case(self):
        Product.objects.create(name="Tata Tea 50gms", code="Tata_Tea_100gms")
        response = self.client.post(
            "/master/product/add/",
            {"name": "tata tea 50gms", "code": "tata_tea_100gms"},
        )
        self.assertContains(
            response, "tata tea 50gms is already a product name", status_code=400
        )
        self.assertContains(
            response, "tata_tea_100gms is already a product code", status_code=400
        )

    # check if code accepts only characters and numbers. no spaces or special characters
    def test_only_alphanumeric_and_underscore(self):
        # cannot contain space
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 100gms", "code": "tat tea 100gms"},
        )
        self.assertContains(
            response,
            "Product code can only be alphanumeric or underscore",
            status_code=400,
        )

        # cannot contain hyphen
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 100gms", "code": "tata-tea-100gms"},
        )
        self.assertContains(
            response,
            "Product code can only be alphanumeric or underscore",
            status_code=400,
        )

        # can contain underscore and numbers
        response = self.client.post(
            "/master/product/add/",
            {"name": "Tata Tea 100gms", "code": "tata_tea_100gms"},
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            (reverse("smplshop.master:product_list") + "?new_code=tata_tea_100gms"),
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Tata Tea 100gms product added successfully")
