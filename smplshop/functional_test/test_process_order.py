from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from faker import Faker

from smplshop.master.tests.factory import StoreFactory
from smplshop.shop.tests.factory import OrderFactory, OrderItemFactory
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
        self.password = fake.password()
        self.user = UserFactory.create(password=self.password)
        self.store1orders = OrderFactory.create_batch(5, store=self.store1)
        for i in range(0, 5):
            OrderItemFactory.create_batch(6, order=self.store1orders[i])

    def test_process_an_order(self):
        page = self.browser.new_page()

        # user logs into his screen
        page.goto("{}{}".format(self.live_server_url, "/accounts/login/"))
        page.get_by_placeholder("E-mail address").fill(self.user.email)
        page.get_by_placeholder("Password").fill(self.password)
        page.get_by_role("button", name="Sign In").click()

        # user clicks on orders from the menu
        page.get_by_role("button", name="Transaction Data").click()
        page.get_by_role("link", name="Orders").click()
        self.assertEqual(
            page.url, "{}{}".format(self.live_server_url, "/transaction/orders/")
        )

        # user sees a number or orders that have been placed
        # user clicks the first order
        order_container = page.locator(
            selector=".accordion-item", has_text=str(self.store1orders[0].uuid)
        )

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Placed"
            ).is_visible(),
            True,
        )

        order_container.locator(
            selector="button", has_text=str(self.store1orders[0].uuid)
        ).click()

        # user sees the details of the items requested in the order
        self.confirm_iems_in_order(self.store1orders[0], order_container)
        # user sees an action to accept or cancel the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=True,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )
        # user cancels the first order
        # the system asks for a confirmation
        # user confirms the cancellation
        # user sees that the order is cancelled

        self.cancel_order(order_container)

        # user sees no actions available for the first order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user clicks on the second order
        order_container = page.locator(
            selector=".accordion-item", has_text=str(self.store1orders[1].uuid)
        )

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Placed"
            ).is_visible(),
            True,
        )

        order_container.locator(
            selector="button", has_text=str(self.store1orders[1].uuid)
        ).click()

        # user sees the details of the items requested in the order
        self.confirm_iems_in_order(self.store1orders[1], order_container)
        # user sees an action to accept or cancel the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=True,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user accepts the second order
        # user sees that the order is accepted
        order_container.locator(selector="a", has_text="Accept").click()
        order_container.locator(selector="button", has_text="Order Accepted").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Accepted"
            ).is_visible(),
            True,
        )

        # user sees cancel and ship options are available for the second order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=True,
            deliver_visible=False,
            close_visible=False,
        )

        # user cancels the second order
        self.cancel_order(order_container)

        # user sees no options are available for the second order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user clicks on the third order
        order_container = page.locator(
            selector=".accordion-item", has_text=str(self.store1orders[2].uuid)
        )

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Placed"
            ).is_visible(),
            True,
        )

        order_container.locator(
            selector="button", has_text=str(self.store1orders[2].uuid)
        ).click()

        # user sees the details of the items requested in the third order
        self.confirm_iems_in_order(self.store1orders[2], order_container)

        # user sees an action to accept or cancel the third order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=True,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user accepts the third order
        # user sees that the order is accepted
        order_container.locator(selector="a", has_text="Accept").click()
        order_container.locator(selector="button", has_text="Order Accepted").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Accepted"
            ).is_visible(),
            True,
        )

        # user sees cancel and ship options are available for the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=True,
            deliver_visible=False,
            close_visible=False,
        )

        # user ships the order
        # user sees that the order has been shipped
        order_container.locator(selector="a", has_text="Ship").click()
        order_container.locator(selector="button", has_text="Order Shipped").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Shipped"
            ).is_visible(),
            True,
        )

        # user sees cancel and deliver options are available for the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=True,
            close_visible=False,
        )

        # user selects the cancel option
        # user sees that the status has chanced to cancelled.
        self.cancel_order(order_container)

        # user sees no options are available for the third order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user clicks on the fourth order
        order_container = page.locator(
            selector=".accordion-item", has_text=str(self.store1orders[3].uuid)
        )

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Placed"
            ).is_visible(),
            True,
        )

        order_container.locator(
            selector="button", has_text=str(self.store1orders[3].uuid)
        ).click()

        # user sees the details of the items requested in the order
        self.confirm_iems_in_order(self.store1orders[3], order_container)

        # user sees an action to accept or cancel the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=True,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user accepts the fourth order
        # user sees that the order is accepted
        order_container.locator(selector="a", has_text="Accept").click()
        order_container.locator(selector="button", has_text="Order Accepted").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Accepted"
            ).is_visible(),
            True,
        )

        # user sees cancel and ship options are available for the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=True,
            deliver_visible=False,
            close_visible=False,
        )

        # user ships the order
        # user sees that the order has been shipped
        order_container.locator(selector="a", has_text="Ship").click()
        order_container.locator(selector="button", has_text="Order Shipped").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Shipped"
            ).is_visible(),
            True,
        )

        # user sees cancel and deliver options are available for the fourth order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=True,
            close_visible=False,
        )

        # user selects the cancel option
        # user sees that the status has chanced to cancelled.
        self.cancel_order(order_container)

        # user sees no options are available for the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user clicks on the fifth order
        order_container = page.locator(
            selector=".accordion-item", has_text=str(self.store1orders[4].uuid)
        )

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Placed"
            ).is_visible(),
            True,
        )

        order_container.locator(
            selector="button", has_text=str(self.store1orders[4].uuid)
        ).click()

        # user sees the details of the items requested in the fifth order
        self.confirm_iems_in_order(self.store1orders[4], order_container)

        # user sees an action to accept or cancel the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=True,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

        # user accepts the fifth order
        # user sees that the order is accepted
        order_container.locator(selector="a", has_text="Accept").click()
        order_container.locator(selector="button", has_text="Order Accepted").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Accepted"
            ).is_visible(),
            True,
        )

        # user sees cancel and ship options are available for the order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=True,
            deliver_visible=False,
            close_visible=False,
        )

        # user ships the order
        # user sees that the order has been shipped
        order_container.locator(selector="a", has_text="Ship").click()
        order_container.locator(selector="button", has_text="Order Shipped").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Shipped"
            ).is_visible(),
            True,
        )

        # user sees cancel and deliver options are available for the fifth order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=True,
            ship_visible=False,
            deliver_visible=True,
            close_visible=False,
        )

        # user selects the deliver option for the fifth order and clicks on it
        # user sees that the status has chanced to delivered.
        order_container.locator(selector="a", has_text="Deliver").click()
        order_container.locator(
            selector="button", has_text="Order Delivered"
        ).wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Delivered"
            ).is_visible(),
            True,
        )

        # user sees close option only available for the fifth order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=True,
        )

        # user selects the close option for the fifth order and clicks on it
        # user sees that the status has chanced to delivered.
        order_container.locator(selector="a", has_text="Close").click()
        order_container.locator(selector="button", has_text="Order Closed").wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Closed"
            ).is_visible(),
            True,
        )

        # user sees there are no further options available for the fifth order
        self.confirm_actions_user_sees_for_order(
            order_container,
            accept_visible=False,
            cancel_visible=False,
            ship_visible=False,
            deliver_visible=False,
            close_visible=False,
        )

    def cancel_order(self, order_container):
        order_container.locator(selector="a", has_text="Cancel").click()
        order_container.locator(
            selector="button", has_text="Order Cancelled"
        ).wait_for()

        self.assertEqual(
            order_container.locator(
                selector="button", has_text="Order Cancelled"
            ).is_visible(),
            True,
        )

    def confirm_iems_in_order(self, storeorders, order_container):
        for item in storeorders.orderitem_set.all():
            order_item_container = order_container.locator(
                selector="tr", has_text=str(item.product)
            )
            self.assertIn(
                str(item.product),
                order_item_container.locator("id=product_name").inner_html(),
            )
            self.assertIn(
                str(item.quantity),
                order_item_container.locator("id=quantity").inner_html(),
            )
            self.assertIn(
                f"{item.price:.2f}",
                order_item_container.locator("id=price").inner_html(),
            )
            self.assertIn(
                f"{item.total_price:.2f}",
                order_item_container.locator("id=total_price").inner_html(),
            )

    def confirm_actions_user_sees_for_order(
        self,
        order_container,
        accept_visible,
        cancel_visible,
        ship_visible,
        deliver_visible,
        close_visible,
    ):
        self.assertEqual(
            order_container.locator(selector="a", has_text="Accept").is_visible(),
            accept_visible,
        )
        self.assertEqual(
            order_container.locator(selector="a", has_text="Cancel").is_visible(),
            cancel_visible,
        )
        self.assertEqual(
            order_container.locator(selector="a", has_text="Ship").is_visible(),
            ship_visible,
        )
        self.assertEqual(
            order_container.locator(selector="a", has_text="Deliver").is_visible(),
            deliver_visible,
        )
        self.assertEqual(
            order_container.locator(selector="a", has_text="Close").is_visible(),
            close_visible,
        )
