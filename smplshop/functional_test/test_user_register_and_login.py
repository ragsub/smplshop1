import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver import ChromeOptions


@override_settings(ALLOWED_HOSTS=["*"])
class RegisterAndLogin(StaticLiveServerTestCase):
    host = "0.0.0.0"

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.host = socket.gethostbyname(socket.gethostname())
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        super().tearDownClass()

    def test_login(self):
        self.driver.get(self.live_server_url)
        self.assertIn("SmplShop", self.driver.title)
