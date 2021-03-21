from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time


def skip_cookies(browser):
    """ Given a selenium.webdriver.WebDriver accept the cookies screen at the loading of bonk.io"""
    cookies_frame = browser.find_element_by_id("sp_message_iframe_403823")
    browser.switch_to.frame(cookies_frame)
    driver.find_element_by_xpath("//button[text()='Accept']").click()


BONK_URL = "http://bonk.io"
DELAY = 5


def setup_browser(driver_type="chrome"):
    """ Create a webdriver instance browser """
    if driver_type == "chrome":
        browser = webdriver.Chrome()
    else:
        raise NotImplementedError()

    browser.get(BONK_URL)
    return browser


def switch_to_mainframe(browser):
    """ Go to parent iframe of html """
    browser.switch_to.parent_frame()


def switch_to_frame(browser, frame_name):
    """ Switch to an iframe """
    browser.switch_to.frame(frame_name)


def wait_until_loaded(browser, by_what, value):
    """ Select an element by a selenium.webdriver.common.by.By method and wait until it loads"""
    try:
        elem = WebDriverWait(browser, DELAY).until(EC.presence_of_element_located((by_what, value)))
    except TimeoutException:
        print("Loading took too much time!")


def wait_until_clickable(browser, by_what, value):
    """ Select an element by a selenium.webdriver.common.by.By method and wait until it can be clicked"""
    try:
        elem = WebDriverWait(browser, DELAY).until(EC.element_to_be_clickable((by_what, value)))
    except TimeoutException:
        print("Loading took too much time!")


def wait_until_clickable_and_click(browser, by_what, value):
    """ Select an element, wait for it to be clickable and then click """
    wait_until_clickable(browser, by_what, value)
    if by_what == By.XPATH:
        browser.find_element_by_xpath(value).click()
    elif by_what == By.ID:
        browser.find_element_by_id(value).click()
    else:
        raise NotImplementedError()


def from_main_menu_to_game():
    """ Create a browser, login and queue up for a game. """
    browser = setup_browser()

    # Remove cookies
    time.sleep(0.1)
    wait_until_clickable(browser, By.ID, 'sp_message_iframe_403823')
    switch_to_frame(browser, 'sp_message_iframe_403823')

    wait_until_clickable_and_click(browser, By.XPATH, "//button[text()='Accept']")

    # Switch to game frame
    time.sleep(1.0)
    switch_to_mainframe(browser)
    switch_to_frame(browser, 'maingameframe')

    # Login/Register button
    wait_until_clickable_and_click(browser,  By.ID, 'guestOrAccountContainer_accountButton')

    # enter username and password
    time.sleep(0.1)
    wait_until_clickable(browser, By.ID, 'loginwindow_password')
    username = 'DefntlyNotAbot'
    password = 'abc123'
    browser.find_element_by_id('loginwindow_username').send_keys(username)
    browser.find_element_by_id('loginwindow_password').send_keys(password)
    # CLICK LOGIN
    wait_until_clickable_and_click(browser, By.ID, 'loginwindow_submitbutton')

    # Click Quickplay
    wait_until_clickable_and_click(browser,  By.ID, 'classic_mid_quickplay')

    # Play a classic gamemode game
    element = browser.find_element_by_id('quickPlayWindow_ClassicButton')
    browser.execute_script("arguments[0].click();", element)

    # Uncomment and place a breakpoint to take a screenshot at will
    # browser.save_screenshot("test.png")

    return browser
