import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestServerRoutes:
    """
    As said in confest.py, the live_server fixture has unresolved issues on Windows and
    Mac so we will not use it for now. Instead we will start the server manually before
    running the tests.
    """

    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)

    def teardown_method(self, method):
        self.driver.close()

    def test_anonymous_user_checks_clubs_list(self):
        self.driver.get("http://127.0.0.1:5000")
        assert "GUDLFT Registration" in self.driver.title
        time.sleep(1)
        display_board_link = self.driver.find_element(By.LINK_TEXT, "here")
        display_board_link.click()
        assert "Clubs list" in self.driver.title
        time.sleep(2)

    def test_valid_purchase_process(self):
        self.driver.get("http://127.0.0.1:5000")
        assert "GUDLFT Registration" in self.driver.title
        email_field = self.driver.find_element(By.NAME, "email")
        time.sleep(1)
        email_field.send_keys("john@simplylift.co")
        time.sleep(1)
        email_field.submit()
        time.sleep(1)
        assert "Summary" in self.driver.title
        time.sleep(1)
        first_book_link = self.driver.find_element(By.XPATH, "//ul/li/a")
        first_book_link.click()
        time.sleep(1)
        assert "Booking for " in self.driver.title
        places_field = self.driver.find_element(By.NAME, "places")
        places_field.send_keys("5")
        time.sleep(1)
        places_field.submit()
        time.sleep(1)
        assert self.driver.current_url == "http://127.0.0.1:5000/purchasePlaces"
        current_page_html = self.driver.page_source
        assert "Great - booking complete!" in current_page_html
        time.sleep(2.5)
