from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from random import randint
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import StringIO



chrome_options = Options()
chrome_options.add_argument("--window-size=1080,1080")
# chrome_options.add_argument("--headless")

try:
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get('https://bonk.io/')

    delay=10#seconds
    #REMOVE COKIES
    time.sleep(0.1)
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'sp_message_iframe_403823')))
    except TimeoutException:
        print("Loading took too much time!")
    # gameframe = browser.find_element_by_id('maingameframe')
    browser.switch_to.frame(browser.find_element_by_id("sp_message_iframe_403823"))
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Accept']")))
    except TimeoutException:
        print("Loading took too much time!")
    browser.find_element_by_xpath("//button[text()='Accept']").click()


    #click login
    time.sleep(0.1)
    browser.switch_to.parent_frame()
    browser.switch_to.frame('maingameframe')
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'guestOrAccountContainer_accountButton')))
    except TimeoutException:
        print("Loading took too much time!")
    browser.find_element_by_id('guestOrAccountContainer_accountButton').click()


    #pass username and password
    time.sleep(0.1)
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'loginwindow_password')))
    except TimeoutException:
        print("Loading took too much time!")
    username='DefntlyNotAbot'
    password='abc123'
    browser.find_element_by_id('loginwindow_username').send_keys(username)
    browser.find_element_by_id('loginwindow_password').send_keys(password)
    #CLICK LOGIN
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'loginwindow_submitbutton')))
    except TimeoutException:
        print("Loading took too much time!")
    browser.find_element_by_id('loginwindow_submitbutton').click()

    # #CLICK SKIN
    # try:
    #     myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'classic_mid_skins')))
    # except TimeoutException:
    #     print("Loading took too much time!")
    # browser.find_element_by_id('classic_mid_skins').click()


    #CLICK PLAY
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'classic_mid_quickplay')))
    except TimeoutException:
        print("Loading took too much time!")
    browser.find_element_by_id('classic_mid_quickplay').click()

    #SELECT GAME MODE
    try:
        myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'quickPlayWindow_ClassicButton')))
    except TimeoutException:
        print("Loading took too much time!")
    element = browser.find_element_by_id('quickPlayWindow_ClassicButton')
    browser.execute_script("arguments[0].click();", element)
    browser.save_screenshot("test.png")

    #SAVE FRAME
    element = browser.find_element_by_id('gamerenderer')
    crop_points = browser.execute_script("""
        var r = arguments[0].getBoundingClientRect();
        return [r.left, r.top, r.left + r.width, r.top + r.height];
        """, element)

    for i in range(1000):
        t = time.time()
        element.screenshot_as_png
        browser.get_screenshot_as_png()
        print(time.time()-t)
    print()
except:
    browser.close()
    exit(1)
#DO ACTION
ActionChains(browser).key_down("w").perform()
print()