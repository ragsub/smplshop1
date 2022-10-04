import re
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By


@override_settings(ALLOWED_HOSTS=["*"])
class RegisterAndLogin(StaticLiveServerTestCase):
    host = "0.0.0.0"

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.host = socket.gethostbyname(socket.gethostname())
        options = ChromeOptions()
        # options.add_argument("--no-sandbox")
        self.driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
        self.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        super().tearDownClass()

    def test_signup_and_login(self):
        # user visits the home page
        self.driver.get(self.live_server_url)
        # she sees that the page has loaded and the company name is smplshop
        self.assertIn("SmplShop", self.driver.title)
        # she is impressed with the value on offer and decides to sign up.
        # she looks for the signup link and finds it.
        self.assertIn("Sign Up", self.driver.page_source)
        # she clicks on the Sign up link.
        self.driver.find_element(By.LINK_TEXT, "Sign Up").click()

        # she confirms that the sign up page has loaded
        self.assertIn("Sign Up", self.driver.title)
        # she fills in the details required such as user name, email, password
        user = "krishna"
        to_email = "admin@krishna.com"
        password = "smplshop"
        self.driver.find_element(By.ID, "id_username").send_keys(user)
        self.driver.find_element(By.ID, "id_email").send_keys(to_email)
        self.driver.find_element(By.ID, "id_password1").send_keys(password)
        self.driver.find_element(By.ID, "id_password2").send_keys(password)
        # she submits the form
        self.driver.find_element(By.ID, "id_submit").click()
        # ActionChains(self.driver).move_to_element(button_element).click(
        #     button_element
        # ).perform()

        # she sees that it has sent an email for her to confirm the signup.
        self.assertIn("Verify your e-mail address", self.driver.page_source)
        self.assertIn(to_email, self.driver.page_source)
        self.assertIn(to_email, mail.outbox[0].to)

        # she checks the email for the link and clicks on it
        url = re.search(r"(?P<url>https?://[^\s]+)", mail.outbox[0].body).group("url")
        self.driver.get(url)

        # she sees that the link has taken her to a page asking her to confirm
        self.assertIn("Confirm your e-mail address", self.driver.page_source)
        # she confirms that the email is hers
        self.driver.find_element(By.ID, "id_submit").click()

        # she is redirected to the login screen
        self.assertIn(to_email, self.driver.page_source)
        self.assertIn("Sign In", self.driver.page_source)

        # she inputs her credentials and clicks on submit
        self.driver.find_element(By.ID, "id_login").send_keys(to_email)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.ID, "id_submit").click()

        # she is in the user profile page
        self.assertIn(to_email, self.driver.page_source)
        self.assertIn("success", self.driver.page_source)

        # she sees a signs out button and cliks it to signout of the system
        self.assertIn("Sign Out", self.driver.page_source)
        self.driver.find_element(By.LINK_TEXT, "Sign Out").click()
        # the system asks for a confirmation and she confirms
        self.assertIn("Are you sure", self.driver.page_source)
        self.driver.find_element(By.ID, "id_submit").click()

        # she is signed out of the system
        self.assertIn("signed out", self.driver.page_source)
