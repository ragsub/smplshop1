import urllib
import uuid

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import resolve, reverse

from smplshop.functional_test.faker import fake
from smplshop.master.tests.factory import StoreFactory
from smplshop.shop.tests.factory import OrderFactory
from smplshop.users.tests.factory import UserFactory


class TestViewAndURL(TestCase):
    def test_url_to_view(self):
        resolver = resolve("/transaction/order/status/")
        self.assertEqual(resolver.view_name, "smplshop.transaction:change_order_status")

    def test_view_to_url(self):
        url = reverse("smplshop.transaction:change_order_status")
        self.assertEqual(url, "/transaction/order/status/")


class TestLoginAndNegativeCasesForPlaced(TestCase):
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
        self.store1 = StoreFactory.create()
        self.order1 = OrderFactory.create(store=self.store1)

    def test_after_login_to_accept(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to accepted"
            ),
        )

    def test_after_login_to_cancel(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=cancel",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to cancelled"
            ),
        )

    def test_before_login(self):
        self.client.logout()
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            "%s%s%s%s"
            % (
                "/accounts/login/?next=/transaction/order/status/",
                urllib.parse.quote_plus("?order_uuid="),
                self.order1.uuid,
                urllib.parse.quote_plus("&change_status=accept"),
            ),
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_blank_order_uuid(self):
        response = self.client.get(
            "{}{}".format("/transaction/order/status/?", "change_status=accept")
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}".format("Order id and change_status has to be filled"),
        )

    def test_blank_change_status(self):
        response = self.client.get(
            "{}{}".format("/transaction/order/status/?order_uuid=", str(uuid.uuid4()))
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}".format("Order id and change_status has to be filled"),
        )

    def test_incorrect_order_uuid(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                str(uuid.uuid4()),
                "&change_status=accept",
            )
        )
        self.assertContains(
            response, "No Order matches the given query.", status_code=404
        )

    def test_incorrect_change_status(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=place",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}".format("Status place is not an allowed value"),
        )

    def test_incorrect_status_placed_to_ship(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=ship",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be shipped"),
        )

    def test_incorrect_status_placed_to_deliver(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=deliver",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be delivered"),
        )

    def test_incorrect_status_placed_to_closed(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=close",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be closed"),
        )


class TestPositiveNegativeCasesForAccepted(TestCase):
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
        self.store1 = StoreFactory.create()
        self.order1 = OrderFactory.create(store=self.store1, status="accepted")

    def test_change_from_accept_to_ship(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=ship",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to shipped"
            ),
        )

    def test_change_from_accept_to_cancel(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=cancel",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to cancelled"
            ),
        )

    def test_incorrect_status_accept_to_deliver(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=deliver",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be delivered"),
        )

    def test_incorrect_status_accept_to_close(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=close",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be closed"),
        )

    def test_incorrect_status_accept_to_accept(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be accepted"),
        )


class TestPositiveNegativeCasesForShipped(TestCase):
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
        self.store1 = StoreFactory.create()
        self.order1 = OrderFactory.create(store=self.store1, status="shipped")

    def test_change_from_ship_to_delivered(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=deliver",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to delivered"
            ),
        )

    def test_change_from_ship_to_cancel(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=cancel",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format(
                "Status of order ", self.order1.uuid, " updated to cancelled"
            ),
        )

    def test_incorrect_status_ship_to_accept(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be accepted"),
        )

    def test_incorrect_status_ship_to_close(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=close",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be closed"),
        )

    def test_incorrect_status_ship_to_ship(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=ship",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be shipped"),
        )


class TestPositiveNegativeCasesForDelivered(TestCase):
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
        self.store1 = StoreFactory.create()
        self.order1 = OrderFactory.create(store=self.store1, status="delivered")

    def test_change_from_deliver_to_closed(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=close",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Status of order ", self.order1.uuid, " updated to closed"),
        )

    def test_incorrect_status_deliver_to_accept(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be accepted"),
        )

    def test_incorrect_status_deliver_to_ship(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=ship",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be shipped"),
        )

    def test_incorrect_status_deliver_to_deliver(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=deliver",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be delivered"),
        )

    def test_incorrect_status_deliver_to_cancel(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=cancel",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be cancelled"),
        )


class TestPositiveNegativeCasesForClosed(TestCase):
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
        self.store1 = StoreFactory.create()
        self.order1 = OrderFactory.create(store=self.store1, status="closed")

    def test_incorrect_status_closed_to_accept(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=accept",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be accepted"),
        )

    def test_incorrect_status_closed_to_ship(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=ship",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be shipped"),
        )

    def test_incorrect_status_closed_to_deliver(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=deliver",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be delivered"),
        )

    def test_incorrect_status_closed_to_cancel(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=cancel",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be cancelled"),
        )

    def test_incorrect_status_closed_to_closed(self):
        response = self.client.get(
            "{}{}{}".format(
                "/transaction/order/status/?order_uuid=",
                self.order1.uuid,
                "&change_status=close",
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, "/transaction/orders/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "{}{}{}".format("Order ", self.order1.uuid, " cannot be closed"),
        )
