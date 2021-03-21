from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from browser_automation import from_main_menu_to_game

BONK_URL = "http://bonk.io"
DELAY = 5


def setup_browser(driver_type="chrome", headless=False):
    if driver_type == "chrome":
        driver = webdriver.Chrome()
    else:
        raise NotImplementedError()

    browser = webdriver.Chrome()
    browser.get(BONK_URL)
    return browser


class GameEngine:
    def __init__(self):
        self.browser = setup_browser()
        self.event_collector = None

    def reset_browser(self):
        del self.browser
        self.browser = setup_browser()

    def start_game(self):
        pass
