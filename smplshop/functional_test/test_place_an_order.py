from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from faker import Faker

from smplshop.master.tests.factory import ProductInStoreFactory, StoreFactory
from smplshop.shop.models import Order
from smplshop.users.tests.factory import UserFactory

from .common import SetUpPlayWrightMixin

fake = Faker()
Faker.seed(23)


@override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
class TestOrderPlacement(SetUpPlayWrightMixin, StaticLiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.store1 = StoreFactory.create()
        self.store2 = StoreFactory.create()
        self.store1products = ProductInStoreFactory.create_batch(50, store=self.store1)
        self.store2products = ProductInStoreFactory.create_batch(50, store=self.store2)
        self.password = fake.password()
        self.user = UserFactory.create(password=self.password)

    def test_place_an_order(self):
        page = self.browser.new_page()

        # user visits the site of the store
        page.goto(
            "{}{}{}{}".format(self.live_server_url, "/shop/", self.store1.code, "/")
        )

        # a lot of products are displayed
        for i in range(0, 50):
            self.assertIn(str(self.store1products[i].product), page.content())

        # user adds multiple products to the cart
        # the cart icon reflects that the item has been added to cart

        items = [25, 49, 0, 49, 48, 49]
        count = [1, 1, 1, 2, 1, 3]
        for i in range(0, 6):
            div = page.locator(
                "id=shop_item", has_text=self.store1products[items[i]].product.name
            )
            div.get_by_role("link").click()
            self.assertIn("In Cart:" + str(count[i]), div.inner_html())

        # user clicks on the cart to view it
        page.get_by_role("link", name="Cart (current)").click()
        self.assertEqual(
            page.url,
            "{}{}{}{}".format(
                self.live_server_url, "/shop/", self.store1.code, "/cart/"
            ),
        )

        # the cart shows the 4 items that were added to it
        items = [25, 49, 0, 48]
        count = [1, 3, 1, 1]
        total_cart_price = 0.0
        for i in range(0, 4):
            div = page.locator(
                "tr", has_text=self.store1products[items[i]].product.name
            )

            self.assertIn(str(count[i]), div.locator("id=quantity").inner_html())
            self.assertIn(
                self.store1products[items[i]].price,
                div.locator("id=price").inner_html(),
            )
            total_price = float(self.store1products[items[i]].price) * float(count[i])
            total_cart_price = total_cart_price + total_price

            self.assertIn(
                str(total_price),
                div.locator("id=total_price").inner_html(),
            )
        self.assertIn(
            str(total_cart_price), page.locator("id=total_cart_price").inner_html()
        )

        # user clicks the order button
        page.get_by_role("link", name="Order").click()

        # the system prompts to login before continuing
        self.assertEqual(
            page.url,
            "%s%s%s%s"
            % (
                self.live_server_url,
                "/accounts/login/?next=/shop/",
                self.store1.code,
                "/cart/order/",
            ),
        )

        # user logs in to the system as buyer
        page.get_by_placeholder("E-mail address").fill(self.user.email)
        page.get_by_placeholder("Password").fill(self.password)
        page.get_by_role("button", name="Sign In").click()

        # page redirects to the list of active orders for the user
        self.assertEqual(
            page.url,
            "%s%s%s%s"
            % (
                self.live_server_url,
                "/shop/",
                self.store1.code,
                "/orders/",
            ),
        )

        new_order = Order.objects.get(user=self.user)

        # order placed successfully message is shown on top
        self.assertIn(
            "{}{}{}".format("Order ", str(new_order.uuid), " created"), page.content()
        )
        self.assertIn(
            "{}{}{}".format("Successfully signed in as ", self.user.username, "."),
            page.content(),
        )

        page.locator("id=order_number", has_text=str(new_order.uuid)).click()

        # the order shows the 4 items that were added to it
        items = [25, 49, 0, 48]
        count = [1, 3, 1, 1]
        total_cart_price = 0.0
        for i in range(0, 4):
            div = page.locator(
                "tr", has_text=self.store1products[items[i]].product.name
            )

            self.assertIn(str(count[i]), div.locator("id=quantity").inner_html())
            self.assertIn(
                self.store1products[items[i]].price,
                div.locator("id=price").inner_html(),
            )
            total_price = float(self.store1products[items[i]].price) * float(count[i])
            total_cart_price = total_cart_price + total_price

            self.assertIn(
                str(total_price),
                div.locator("id=total_price").inner_html(),
            )
