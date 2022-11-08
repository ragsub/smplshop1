from random import randint

from django.conf import settings
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.models import ProductInStore
from smplshop.users.tests.factory import UserFactory

from .factory import ProductFactory, ProductInStoreFactory, StoreFactory


class TestProductInStoreListView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

        cls.fields = ["store", "product", "price"]
        store1 = StoreFactory.create()
        store2 = StoreFactory.create()
        ProductInStoreFactory.create_batch(size=50, store=store1)
        ProductInStoreFactory.create_batch(size=25, store=store2)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/store/product/")
        self.assertEqual(resolver.view_name, "smplshop.master:product_in_store_list")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:product_in_store_list")
        self.assertEqual(url, "/master/store/product/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/store/product/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/store/product/")
        self.assertTemplateUsed(
            response=response, template_name="master/product_in_store_list.html"
        )

    # check if all records are shown
    def test_pagination(self):

        all_product_in_store = (
            ProductInStore.objects.all()
            .values_list(*self.fields)
            .annotate(new=Value(""))
        )
        pages = Paginator(all_product_in_store, settings.ITEMS_PER_PAGE)

        response = self.client.get("/master/store/product/")
        page_1 = pages.page(1)
        self.assertQuerysetEqual(page_1.object_list, response.context["object_list"])

        page_last = pages.page(pages.num_pages)
        response = self.client.get(
            "/master/store/product/?page=" + str(pages.num_pages)
        )
        self.assertQuerysetEqual(page_last.object_list, response.context["object_list"])

        page_n = pages.page(randint(1, pages.num_pages))
        response = self.client.get("/master/store/product/?page=" + str(page_n.number))
        self.assertQuerysetEqual(page_n.object_list, response.context["object_list"])

    # check if new records are identified
    def test_new_records(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.get(
            "/master/store/product/?new_code=" + str(product_in_store.uuid)
        )
        self.assertContains(response, str(product_in_store.store))
        self.assertContains(response, str(product_in_store.product))
        self.assertContains(response, str(product_in_store.price))
        self.assertContains(response, "New")

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/store/product/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)


class TestProductInStoreCreateView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)
        store1 = StoreFactory.create()
        store2 = StoreFactory.create()
        ProductInStoreFactory.reset_sequence(0)
        ProductInStoreFactory.create_batch(size=50, store=store1)
        ProductInStoreFactory.create_batch(size=25, store=store2)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    # login required to access page
    def test_login_required(self):
        self.client.logout()
        response = self.client.get("/master/store/product/add/")
        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    # url resolves to right name
    def test_url_to_name(self):
        resolver = resolve("/master/store/product/add/")
        self.assertEqual(resolver.view_name, "smplshop.master:product_in_store_add")

    # name resolves to right url
    def test_name_to_url(self):
        url = reverse("smplshop.master:product_in_store_add")
        self.assertEqual(url, "/master/store/product/add/")

    # page is loaded
    def test_correct_path(self):
        response = self.client.get("/master/store/product/add/")
        self.assertEqual(200, response.status_code)

    # correct template is used
    def test_correct_template(self):
        response = self.client.get("/master/store/product/add/")
        self.assertTemplateUsed(
            response=response, template_name="master/product_in_store_add.html"
        )

    # check if record can be added
    def test_add_record(self):
        store1 = StoreFactory.create()
        product1 = ProductFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {"store": store1.name, "product": product1.name, "price": 55},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        product_in_store = ProductInStore.objects.get(
            Q(store=store1) & Q(product=product1)
        )
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            (
                reverse("smplshop.master:product_in_store_list")
                + "?new_code="
                + str(product_in_store.uuid)
            ),
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            str(product_in_store.product)
            + " in "
            + str(product_in_store.store)
            + " added successfully",
        )

    # check if duplicate record of all 3 is rejeced
    def test_duplicate_store_product_price_record(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "store": product_in_store.store,
                "product": product_in_store.product,
                "price": product_in_store.price,
            },
        )
        self.assertContains(
            response,
            "Product In Store with this Store and Product already exists.",
            status_code=400,
        )

    # check if duplicate record of store and product is rejected
    def test_duplicate_store_and_product_record(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "store": product_in_store.store,
                "product": product_in_store.product,
                "price": 32,
            },
        )
        self.assertTemplateUsed("genericview/product_in_store_add.html")

        self.assertContains(
            response,
            "Product In Store with this Store and Product already exists.",
            status_code=400,
        )

    # check if duplicate record of store is accepted when product is different
    def test_duplicate_store_record(self):
        product = ProductFactory.create()
        product_in_store1 = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "store": product_in_store1.store,
                "product": product,
                "price": 32,
            },
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        product_in_store2 = ProductInStore.objects.get(
            Q(store=product_in_store1.store) & Q(product=product)
        )
        # 302 is redirect status
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            (
                reverse("smplshop.master:product_in_store_list")
                + "?new_code="
                + str(product_in_store2.uuid)
            ),
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            str(product_in_store2.product)
            + " in "
            + str(product_in_store2.store)
            + " added successfully",
        )

    # check if store that is not there in store table is rejected
    def test_invalid_store_case(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "product": product_in_store.product,
                "store": "store1",
                "price": product_in_store.price,
            },
        )
        self.assertContains(
            response,
            "Select a valid choice. That choice is not one of the available choices.",
            status_code=400,
        )

    # check if product that is not there in store table is rejected
    def test_invalid_product_case(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "product": "prod1",
                "store": product_in_store.store,
                "price": product_in_store.price,
            },
        )
        self.assertContains(
            response,
            "Select a valid choice. That choice is not one of the available choices.",
            status_code=400,
        )

    # price cannot be negative
    def test_negative_price(self):
        product_in_store = ProductInStoreFactory.create()
        response = self.client.post(
            "/master/store/product/add/",
            {
                "product": product_in_store.product,
                "store": product_in_store.store,
                "price": -5,
            },
        )

        self.assertContains(
            response,
            "Ensure this value is greater than or equal to 0.0.",
            status_code=400,
        )
