import re
import uuid

from django.contrib.messages import get_messages
from django.db.models import F
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.tests.factory import ProductInStoreFactory, StoreFactory
from smplshop.shop.models import Cart, Order
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
            50, store=self.store1
        )
        self.product_in_store2 = ProductInStoreFactory.create_batch(
            50, store=self.store2
        )
        self.product_in_store3 = ProductInStoreFactory.create_batch(
            50, store=self.store3
        )

        self.client.login(username=self.user.username, password=self.password)

    def test_cart_after_login(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertEqual(response.status_code, 200)

    def test_cart_before_login(self):
        self.client.logout()
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertEqual(response.status_code, 200)

    def test_url_resolves_to_view(self):
        resolver = resolve("{}{}{}".format("/shop/", self.store1.code, "/cart/"))
        self.assertEqual(resolver.view_name, "smplshop.shop:cart")

    def test_view_resolves_to_url(self):
        url = reverse("smplshop.shop:cart", kwargs={"shop": self.store1.code})
        self.assertEqual(url, "{}{}{}".format("/shop/", self.store1.code, "/cart/"))

    def test_correct_template(self):
        self.client.get("{}{}{}".format("/shop/", self.store1.code, "/cart/"))
        self.assertTemplateUsed("shop/cart.html")

    def test_cart_queryset_when_empty(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertQuerysetEqual(response.context["object_list"], Cart.objects.none())
        self.assertContains(response, "Cart is empty")

    def test_cart_queryset_with_incorrect_cart(self):
        session = self.client.session
        session[self.store1.code] = str(uuid.uuid4())
        session.save()
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "No Cart matches the given query.", status_code=404
        )

    def test_cart_queryset_with_empty_cart(self):
        cart = CartFactory.create_batch(50, store=self.store1)
        session = self.client.session
        session[self.store1.code] = str(cart[0].uuid)
        session.save()

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertQuerysetEqual(
            response.context["object_list"],
            Cart.objects.filter(uuid=cart[0].uuid, store__code=self.store1.code),
        )

    def test_cart_queryset_with_cart_and_items(self):
        carts = CartFactory.create_batch(50, store=self.store1)
        CartItemFactory.create_batch(10, cart=carts[0])
        CartItemFactory.create_batch(10, cart=carts[1])

        session = self.client.session
        session[self.store1.code] = str(carts[1].uuid)
        session.save()
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/")
        )
        self.assertQuerysetEqual(
            response.context["object_list"],
            Cart.objects.filter(uuid=carts[1].uuid, store__code=self.store1.code)
            .prefetch_related("cartitem_set")
            .annotate(
                product=F("cartitem__product_in_store__product"),
                price=F("cartitem__product_in_store__price"),
                quantity=F("cartitem__quantity"),
            )
            .annotate(total_price=F("price") * F("quantity")),
            ordered=False,
        )
        self.assertEqual(
            response.context["total_cart_price"], carts[1].total_cart_price
        )


class TestPlaceOrder(TestCase):
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
        self.cart1 = CartFactory.create(store=self.store1)
        self.cart2 = CartFactory.create(store=self.store2)
        self.cart3 = CartFactory.create(store=self.store3)
        self.cart1items = CartItemFactory.create_batch(20, cart=self.cart1)
        self.cart2items = CartItemFactory.create_batch(15, cart=self.cart2)
        self.cart3items = CartItemFactory.create_batch(10, cart=self.cart3)
        self.client.login(username=self.user.username, password=self.password)

    def test_order_after_login(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "{}{}{}".format("/shop/", self.store1.code, "/orders/")
        )

    def test_cart_before_login(self):
        self.client.logout()
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "%s%s%s"
            % ("/accounts/login/?next=/shop/", self.store1.code, "/cart/order/"),
        )

    def test_url_resolves_to_view(self):
        resolver = resolve("{}{}{}".format("/shop/", self.store1.code, "/cart/order/"))
        self.assertEqual(resolver.view_name, "smplshop.shop:place_order")

    def test_view_resolves_to_url(self):
        url = reverse("smplshop.shop:place_order", kwargs={"shop": self.store1.code})
        self.assertEqual(
            url, "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )

    def test_do_not_order_empty_cart(self):
        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No items in cart to order")

    def test_do_not_order_cart_with_no_items(self):
        store = StoreFactory.create()
        cart = CartFactory.create(store=store)

        session = self.client.session
        session[store.code] = str(cart.uuid)
        session.save()
        response = self.client.get(
            "{}{}{}".format("/shop/", store.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No items in cart to order")

    def test_do_not_order_cart_for_different_store(self):
        store = StoreFactory.create()
        session = self.client.session
        session[store.code] = str(self.cart1.uuid)
        session.save()
        response = self.client.get(
            "{}{}{}".format("/shop/", store.code, "/cart/order/")
        )
        self.assertEqual(404, response.status_code)
        self.assertContains(
            response, "No Cart matches the given query.", status_code=404
        )

    def test_order_placed_for_cart(self):
        session = self.client.session
        session[self.store2.code] = str(self.cart2.uuid)
        session.save()

        cart_uuid = self.cart2.uuid
        cart_items = list(self.cart2.cartitem_set.all())

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store2.code, "/cart/order/")
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertRegex(str(messages[0]), "^Order .* created$")

        order_uuid = re.search(r"Order (.*?) created", str(messages[0])).group(1)

        new_order = Order.objects.get(store=self.store2, uuid=order_uuid)
        self.assertEqual(new_order.status, "placed")
        self.assertEqual(new_order.orderitem_set.count(), 15)
        for item in cart_items:
            self.assertTrue(
                new_order.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart_uuid))
        self.assertIsNone(response.wsgi_request.session.get(self.store1.code, None))

    def test_second_order_can_be_placed(self):
        cart1_uuid = self.cart1.uuid
        cart1_items = list(self.cart1.cartitem_set.all())

        cart4 = CartFactory.create(store=self.store1)
        cart4_items = CartItemFactory.create_batch(7, cart=cart4)
        cart4_uuid = cart4.uuid
        cart4_items = list(cart4.cartitem_set.all())

        session = self.client.session
        session[self.store1.code] = str(self.cart1.uuid)
        session.save()

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        self.assertIsNone(response.wsgi_request.session.get(self.store1.code, None))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertRegex(str(messages[0]), "^Order .* created$")

        order1_uuid = re.search(r"Order (.*?) created", str(messages[0])).group(1)

        session[self.store1.code] = str(cart4.uuid)
        session.save()

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertRegex(str(messages[1]), "^Order .* created$")

        order4_uuid = re.search(r"Order (.*?) created", str(messages[1])).group(1)

        new_order1 = Order.objects.filter(store=self.store1, uuid=order1_uuid).first()
        self.assertEqual(new_order1.status, "placed")
        self.assertEqual(new_order1.orderitem_set.count(), 20)

        new_order4 = Order.objects.filter(store=self.store1, uuid=order4_uuid).first()
        self.assertEqual(new_order4.status, "placed")
        self.assertEqual(new_order4.orderitem_set.count(), 7)

        for item in cart1_items:
            self.assertTrue(
                new_order1.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart1_uuid).exists())

        for item in cart4_items:
            self.assertTrue(
                new_order4.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart4_uuid).exists())
        self.assertIsNone(response.wsgi_request.session.get(self.store1.code, None))

    def test_placing_three_carts_in_three_shops(self):
        session = self.client.session
        session[self.store1.code] = str(self.cart1.uuid)
        session[self.store2.code] = str(self.cart2.uuid)
        session[self.store3.code] = str(self.cart3.uuid)
        session.save()

        cart1_uuid = self.cart1.uuid
        cart1_items = list(self.cart1.cartitem_set.all())
        cart2_uuid = self.cart2.uuid
        cart2_items = list(self.cart2.cartitem_set.all())
        cart3_uuid = self.cart3.uuid
        cart3_items = list(self.cart3.cartitem_set.all())

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store1.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertRegex(str(messages[0]), "^Order .* created$")
        order1_uuid = re.search(r"Order (.*?) created", str(messages[0])).group(1)

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store2.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertRegex(str(messages[1]), "^Order .* created$")
        order2_uuid = re.search(r"Order (.*?) created", str(messages[1])).group(1)

        response = self.client.get(
            "{}{}{}".format("/shop/", self.store3.code, "/cart/order/")
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 3)
        self.assertRegex(str(messages[2]), "^Order .* created$")
        order3_uuid = re.search(r"Order (.*?) created", str(messages[2])).group(1)

        new_order1 = Order.objects.filter(store=self.store1, uuid=order1_uuid).first()
        self.assertEqual(new_order1.status, "placed")
        self.assertEqual(new_order1.orderitem_set.count(), 20)
        for item in cart1_items:
            self.assertTrue(
                new_order1.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart1_uuid).exists())
        self.assertIsNone(response.wsgi_request.session.get(self.store1.code, None))

        new_order2 = Order.objects.filter(store=self.store2, uuid=order2_uuid).first()
        self.assertEqual(new_order2.status, "placed")
        self.assertEqual(new_order2.orderitem_set.count(), 15)
        for item in cart2_items:
            self.assertTrue(
                new_order2.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart2_uuid).exists())
        self.assertIsNone(response.wsgi_request.session.get(self.store2.code, None))

        new_order3 = Order.objects.filter(store=self.store3, uuid=order3_uuid).first()
        self.assertEqual(new_order3.status, "placed")
        self.assertEqual(new_order3.orderitem_set.count(), 10)
        for item in cart3_items:
            self.assertTrue(
                new_order3.orderitem_set.get(
                    product=item.product_in_store.product,
                    price=item.product_in_store.price,
                    quantity=item.quantity,
                )
            )
        self.assertFalse(Cart.objects.filter(uuid=cart3_uuid).exists())
        self.assertIsNone(response.wsgi_request.session.get(self.store3.code, None))
