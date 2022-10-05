import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver import ChromeOptions


@override_settings(ALLOWED_HOSTS=["*"])
class SetupTests(StaticLiveServerTestCase):
    host = "0.0.0.0"

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.host = socket.gethostbyname(socket.gethostname())
        options = ChromeOptions()
        self.driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
        self.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        super().tearDownClass()
