import re

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from faker import Faker

from smplshop.users.tests.factory import UserFactory

from .common import SetUpPlayWrightMixin

fake = Faker()
Faker.seed(23)


class TestUserSignUp(SetUpPlayWrightMixin, StaticLiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.email = fake.email()
        self.username = fake.user_name()
        self.password = fake.password()
        self.user = UserFactory.create(password=self.password)

    def test_onboarding(self) -> None:
        page = self.browser.new_page()

        # user goes to the home page
        page.goto(self.live_server_url)

        # likes the home page. clicks on the sign up link
        page.get_by_role("link", name="Sign Up").click()
        page.wait_for_url("{}{}".format(self.live_server_url, "/accounts/signup/"))
        self.assertEqual(
            page.url, "{}{}".format(self.live_server_url, "/accounts/signup/")
        )

        # sign up form loads and user fills it in and submits
        page.get_by_placeholder("E-mail address").fill(self.email)
        page.get_by_placeholder("Username").fill(self.username)
        page.get_by_label("Password*").fill(self.password)
        page.get_by_placeholder("Password (again)").fill(self.password)
        page.get_by_role("button", name="Sign Up »").click()

        # the registration is successful. page asks user to confirm by email
        page.wait_for_url(
            "{}{}".format(self.live_server_url, "/accounts/confirm-email/")
        )
        self.assertEqual(
            page.url, "{}{}".format(self.live_server_url, "/accounts/confirm-email/")
        )

        self.assertIn(
            "{}{}{}".format("Confirmation e-mail sent to ", self.email, "."),
            page.content(),
        )
        self.assertIn("Verify your e-mail address", page.content())

        # user checks the email for the link and clicks on it
        url = re.search(
            r"(?P<url>https?://[^\s]+)", mail.outbox[0].body
        ).group(  # type:ignore
            "url"
        )
        page.goto(url)
        # page asks the user to confirm the email
        page.wait_for_url(
            "{}{}".format(self.live_server_url, "/accounts/confirm-email/**")
        )
        self.assertRegex(
            page.url,
            "{}{}".format(self.live_server_url, "/accounts/confirm-email/[.]*"),
        )
        self.assertIn("Confirm your e-mail address", page.content())
        self.assertIn(self.email, page.content())
        # user confirms the email
        page.get_by_role("button", name="Confirm").click()

        # user is redirected to login page
        page.wait_for_url("{}{}".format(self.live_server_url, "/accounts/login/"))
        self.assertEqual(
            page.url, "{}{}".format(self.live_server_url, "/accounts/login/")
        )
        self.assertEqual(page.title(), "Sign In")

        page.get_by_placeholder("E-mail address").fill(self.email)
        page.get_by_placeholder("Password").fill(self.password)

        page.get_by_role("button", name="Sign In").click()

        # user is signed in
        page.wait_for_url(
            "{}{}{}{}".format(self.live_server_url, "/users/", self.username, "/")
        )
        self.assertEqual(
            "{}{}{}{}".format(self.live_server_url, "/users/", self.username, "/"),
            page.url,
        )
        self.assertIn(
            "{}{}{}".format("Successfully signed in as ", self.username, "."),
            page.content(),
        )
        self.assertIn(self.email, page.content())

        # user signs out of the screen
        page.get_by_role("link", name="Sign Out").click()
        page.wait_for_url("{}{}".format(self.live_server_url, "/accounts/logout/"))
        self.assertEqual(
            "{}{}".format(self.live_server_url, "/accounts/logout/"), page.url
        )

        # user confirms the signout
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_url("{}{}".format(self.live_server_url, "/"))
        self.assertEqual("{}{}".format(self.live_server_url, "/"), page.url)

        self.assertIn("You have signed out.", page.content())
