import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Screenshot:
    username = None
    password = None
    login_url = 'https://algotest.in/login'
    live_url = 'https://algotest.in/live'
    options = None
    wait_time = 5
    driver = None

    def __init__(self, data):
        self.username = data['phone_number']
        self.password = data['password']
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')

    def init_login(self):
        print("Login init")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get('https://algotest.in/login')
        time.sleep(self.wait_time)

    def login(self):
        print("Logging In")
        username = self.driver.find_element(By.NAME, "phone")
        password = self.driver.find_element(By.NAME, "password")
        username.send_keys(self.username)
        password.send_keys(self.password)
        login_button = WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_button.click()
        time.sleep(self.wait_time)

    def init_live(self):
        self.driver.get('https://algotest.in/live')
        time.sleep(self.wait_time)

    def init_mtm_graph(self):
        mtm_button = WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'MTM Graph')]"))
        )
        mtm_button.click()
        time.sleep(self.wait_time)

    def take_screenshot(self, path):
        self.driver.set_window_size(1200, 700)
        self.driver.save_screenshot(path)
        self.driver.quit()

    def close(self):
        self.driver.quit()
