from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from smplshop.users.models import User

from .common import SetupTests


@override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
class SetupMasterData(SetupTests):
    driver: webdriver.Chrome

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_name = "krishna"
        cls.password = "smplshop"
        cls.email = "admin@krishna.com"
        cls.new_user = User.objects.create_user(  # type: ignore
            username=cls.user_name,
            email=cls.email,
            password=cls.password,
        )

    def test_setup_masterdata(self):
        # user logsinto the system
        self.driver.get(str(self.live_server_url) + "/accounts/login")
        self.assertIn("Sign In", self.driver.title)
        self.driver.find_element(By.ID, "id_login").send_keys(self.email)
        self.driver.find_element(By.ID, "id_password").send_keys(self.password)
        self.driver.find_element(By.ID, "id_submit").click()

        # user clicks on master data and selects store
        self.assertIn("Master Data", self.driver.page_source)
        self.driver.find_element(By.LINK_TEXT, "Master Data").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Store"))
        ).click()

        # user sees that there are no records in the store
        self.assertIn("Store", self.driver.title)

        # user searches for and finds the add button to add records
        self.assertIn("Add", self.driver.page_source)
        # user clicks on the add button
        self.driver.find_element(By.LINK_TEXT, "Add").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_submit"))
        )

        # a popup shows up with the details required
        self.assertIn("Add Record", self.driver.title)

        # user enters the details of the store such as its name, code and address
        self.driver.find_element(By.ID, "id_name").send_keys("krishna stores")
        self.driver.find_element(By.ID, "id_code").send_keys("krishna")

        # user clicks on the submit button
        self.driver.find_element(By.ID, "id_submit").click()

        WebDriverWait(self.driver, 10).until(EC.title_is("Store"))

        # the dialogue box disappears and the original page shifts to the page where the added record is present
        self.assertIn("Store", self.driver.title)
        self.assertIn("krishna stores", self.driver.page_source)

        # a new badge appears next to the record
        self.assertIn("New", self.driver.page_source)

        # user clicks on master data and selects product
        self.assertIn("Master Data", self.driver.page_source)
        self.driver.find_element(By.LINK_TEXT, "Master Data").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Product"))
        ).click()

        # the product page loads and the user sees that there are no records
        self.assertIn("Product", self.driver.title)

        # user clicks on the add button to add a record
        self.driver.find_element(By.LINK_TEXT, "Add").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_submit"))
        )

        # the add page is visible
        self.assertIn("Add Record", self.driver.title)

        # user enters the product code and product name and presses on the submit button
        self.driver.find_element(By.ID, "id_code").send_keys("tata_tea_50gms")
        self.driver.find_element(By.ID, "id_name").send_keys("Tata Tea 500 gms")
        self.driver.find_element(By.ID, "id_submit").click()

        # the user returns to the product page and sees the new product there
        self.assertIn("Product", self.driver.title)
        self.assertIn("Tata Tea 500 gms", self.driver.page_source)
