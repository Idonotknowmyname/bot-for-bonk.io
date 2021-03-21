from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def skip_cookies(browser):

    cookies_frame = browser.find_element_by_id("sp_message_iframe_403823")
    browser.switch_to.frame(cookies_frame)
    driver.find_element_by_xpath("//button[text()='Accept']").click()


BONK_URL = "http://bonk.io"
DELAY = 5


def setup_browser(driver_type="chrome"):
    if driver_type == "chrome":
        browser = webdriver.Chrome()
    else:
        raise NotImplementedError()

    browser.get(BONK_URL)
    return browser


def switch_to_mainframe(browser):
    browser.switch_to.parent_frame()


def switch_to_frame(browser, frame_name):
    browser.switch_to.frame(frame_name)


def wait_until_loaded(browser, by_what, value):
    try:
        elem = WebDriverWait(browser, DELAY).until(EC.presence_of_element_located((by_what, value)))
    except TimeoutException:
        print("Loading took too much time!")


def wait_until_clickable(browser, by_what, value):
    try:
        elem = WebDriverWait(browser, DELAY).until(EC.element_to_be_clickable((by_what, value)))
    except TimeoutException:
        print("Loading took too much time!")


def wait_until_clickable_and_click(browser, by_what, value):
    wait_until_clickable(browser, by_what, value)
    browser.find_element_by_xpath(value).click()


def from_main_menu_to_game():
    browser = setup_browser()

    wait_until_clickable(browser, By.ID, 'sp_message_iframe_403823')
    switch_to_frame(browser, 'sp_message_iframe_403823')

    wait_until_clickable_and_click(browser, By.XPATH, "//button[text()='Accept']")

    switch_to_mainframe(browser)
    switch_to_frame(browser, 'maingameframe')

    wait_until_clickable_and_click(browser,  By.ID, 'guestOrAccountContainer_accountButton')
    # pass username and password
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'loginwindow_password')))
    except TimeoutException:
        print("Loading took too much time!")
    username = 'DefntlyNotAbot'
    password = 'abc123'
    browser.find_element_by_id('loginwindow_username').send_keys(username)
    browser.find_element_by_id('loginwindow_password').send_keys(password)
    # CLICK LOGIN
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'loginwindow_submitbutton')))
    except TimeoutException:
        print("Loading took too much time!")
    browser.find_element_by_id('loginwindow_submitbutton').click()

    wait_until_clickable_and_click(browser,  By.ID, 'classic_mid_quickplay')

    element = browser.find_element_by_id('quickPlayWindow_ClassicButton')
    browser.execute_script("arguments[0].click();", element)
    browser.save_screenshot("test.png")

    return browser
