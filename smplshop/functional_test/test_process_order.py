from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from faker import Faker

from smplshop.master.tests.factory import StoreFactory
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

    def test_process_an_order(self):
        pass
        # user logs into his screen
        # user clicks on orders from the menu
        # user sees a number or orders that have been placed
        # user clicks the first order
        # user sees the details of the items requested in the order
        # user sees an action to accept or cancel the order
        # user cancels the first order
        # the system asks for a confirmation
        # user confirms the cancellation
        # user sees that the order is cancelled
        # user clicks on the second order
        # user sees the details of the items requested in the second order
        # user sees an action to accept or cancel the order
        # user accepts the order
        # user sees that the order is accepted
        # user sees the option to ship the order or cancel it
        # user cancels the order
        # system asks for a confirmation to cancel
        # user confirms the cancellation
        # user sees the seond order is also cancelled
        # user clicks on the third order
        # user sees the details of the items requested in the third order
        # user sees an action to accept or cancel the order
        # user accepts the order
        # user sees that the order is accepted
        # user sees an action to ship the order or cancel it
        # user sends the item through courier and clicks on ship the order
        # user sees that the status has changed to shipped
        # user sees an action to cancel or mark the order as delivered
        # user clicks on cancel the order
        # user sees that the order has been cancelled
        # user clicks the fourth order
        # user sees the details of the items requested in the fourth order
        # user sees an action to accept or cancel the order
        # user accepts the order
        # user sees an action to ship or cancel the order
        # user clicks on ship the order
        # user sees an action to mark the order as delivered or cancel the order
        # user marks the order as delivered
        # user sees an option to mark the order as closed
        # user confirms that the payment has been received and closes the order
        # there are no further actions to be made on the order
