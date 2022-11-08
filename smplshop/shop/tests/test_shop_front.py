import uuid

from django.db.models import F, FilteredRelation, IntegerField, Q, Value
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.models import ProductInStore
from smplshop.master.tests.factory import ProductInStoreFactory, StoreFactory
from smplshop.shop.models import Cart
from smplshop.users.tests.factory import UserFactory

from .factory import CartFactory, CartItemFactory


class TestShopFront(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self):
        super().setUp()
        fake.unique.clear()
        self.store1 = StoreFactory.create()
        self.store2 = StoreFactory.create()
        self.store3 = StoreFactory.create()
        self.product_in_store1 = ProductInStoreFactory.create_batch(
            20, store=self.store1
        )
        self.product_in_store2 = ProductInStoreFactory.create_batch(
            20, store=self.store2
        )
        self.product_in_store3 = ProductInStoreFactory.create_batch(
            20, store=self.store3
        )

        self.client.login(username=self.user.username, password=self.password)
        self.shop = StoreFactory()

    def test_store_front_after_login(self):
        response = self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertEqual(response.status_code, 200)

    def test_store_front_before_login(self):
        self.client.logout()
        response = self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertEqual(response.status_code, 200)

    def test_url_resolves_to_view(self):
        resolver = resolve("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertEqual(resolver.view_name, "smplshop.shop:shop_front")

    def test_view_resolves_to_url(self):
        url = reverse("smplshop.shop:shop_front", kwargs={"shop": self.store1.code})
        self.assertEqual(url, "{}{}{}".format("/shop/", self.store1.code, "/"))

    def test_correct_template(self):
        self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertTemplateUsed("shop/shop_front.html")

    def test_queryset_with_no_cart(self):
        response = self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        product_in_store1 = ProductInStore.objects.filter(store=self.store1)
        self.assertQuerysetEqual(response.context["object_list"], product_in_store1)

    def test_queryset_with_cart(self):
        cart = CartFactory.create(store=self.store1)
        CartItemFactory.create(cart=cart, product_in_store=self.product_in_store1[0])
        CartItemFactory.create(cart=cart, product_in_store=self.product_in_store1[10])

        product_in_store1 = (
            ProductInStore.objects.filter(store=self.store1)
            .prefetch_related("cart_items")
            .values("uuid", "store", "product", "price")
            .annotate(
                item_in_cart=FilteredRelation(
                    "cart_items", condition=Q(cart_items__cart=cart)
                )
            )
            .annotate(quantity=F("item_in_cart__quantity"))
        )

        session = self.client.session
        session[self.store1.code] = str(cart.uuid)
        session.save()

        response = self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertQuerysetEqual(response.context["object_list"], product_in_store1)  # type: ignore

    def test_queryset_with_cart_but_no_items(self):
        cart = CartFactory.create(store=self.store1)

        product_in_store1 = (
            ProductInStore.objects.filter(store=self.store1)
            .annotate(quantity=Value(None, output_field=IntegerField()))
            .values("uuid", "store", "product", "price", "quantity")
        )

        session = self.client.session
        session[self.store1.code] = str(cart.uuid)
        session.save()

        response = self.client.get("{}{}{}".format("/shop/", self.store1.code, "/"))
        self.assertQuerysetEqual(response.context["object_list"], product_in_store1)  # type: ignore

    def test_empty_shop(self):
        response = self.client.get("{}{}{}".format("/shop/", self.shop.code, "/"))
        self.assertQuerysetEqual(response.context["object_list"], ProductInStore.objects.none())  # type: ignore
        self.assertContains(response, "No items to shop!")


class TestAddToCart(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.password = fake.password()
        cls.user = UserFactory.create(password=cls.password)

    def setUp(self):
        super().setUp()
        fake.unique.clear()
        self.store1 = StoreFactory.create()
        self.store2 = StoreFactory.create()
        self.store3 = StoreFactory.create()
        self.product_in_store1 = ProductInStoreFactory.create_batch(
            20, store=self.store1
        )
        self.product_in_store2 = ProductInStoreFactory.create_batch(
            20, store=self.store2
        )
        self.product_in_store3 = ProductInStoreFactory.create_batch(
            20, store=self.store3
        )

        self.client.login(username=self.user.username, password=self.password)
        self.shop = StoreFactory()

    def test_url_resolves_to_view(self):
        resolver = resolve(
            "%s%s%s%s%s"
            % ("/shop/", self.store1.code, "/cart/add/", str(uuid.uuid4()), "/")
        )
        self.assertEqual(resolver.view_name, "smplshop.shop:add_to_cart")

    def test_view_resolves_to_url(self):
        test_uuid = uuid.uuid4()
        url = reverse(
            "smplshop.shop:add_to_cart",
            kwargs={"shop": self.store1.code, "product_in_store_uuid": test_uuid},
        )
        self.assertEqual(
            url,
            "{}{}{}{}{}".format(
                "/shop/", self.store1.code, "/cart/add/", test_uuid, "/"
            ),
        )

    def test_with_login(self):
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, expected_url="{}{}{}".format("/shop/", self.store1.code, "/")
        )

    def test_without_login(self):
        self.client.logout()
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, expected_url="{}{}{}".format("/shop/", self.store1.code, "/")
        )

    def test_cart_is_added(self):
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )

        store_cookie = response.wsgi_request.session.get(self.store1.code, None)
        cart = Cart.objects.get(store=self.store1)
        self.assertEqual(store_cookie, str(cart.uuid))
        self.assertEqual(
            1,
            cart.cartitem_set.get(product_in_store=self.product_in_store1[1]).quantity,
        )

    def test_second_item_is_added_to_cart(self):
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )
        store_cookie = response.wsgi_request.session.get(self.store1.code, None)
        cart = Cart.objects.get(store=self.store1)
        self.assertEqual(store_cookie, str(cart.uuid))
        self.assertEqual(
            2,
            cart.cartitem_set.get(product_in_store=self.product_in_store1[1]).quantity,
        )

    def test_two_different_items_are_added_to_cart(self):
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[1].uuid),
                "/",
            )
        )
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(self.product_in_store1[5].uuid),
                "/",
            )
        )
        store_cookie = response.wsgi_request.session.get(self.store1.code, None)
        cart = Cart.objects.get(store=self.store1)
        self.assertEqual(store_cookie, str(cart.uuid))
        self.assertEqual(
            1,
            cart.cartitem_set.get(product_in_store=self.product_in_store1[1]).quantity,
        )
        self.assertEqual(
            1,
            cart.cartitem_set.get(product_in_store=self.product_in_store1[5]).quantity,
        )

    def test_wrong_item_is_rejected(self):
        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                str(uuid.uuid4()),
                "/",
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "No ProductInStore matches the given query.", status_code=404
        )

    def test_item_in_wrong_shop_is_rejected(self):

        response = self.client.get(
            "%s%s%s%s%s"
            % (
                "/shop/",
                self.store1.code,
                "/cart/add/",
                self.product_in_store2[0].uuid,
                "/",
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "No ProductInStore matches the given query.", status_code=404
        )
