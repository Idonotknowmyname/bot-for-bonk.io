from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from random import randint


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

browser = webdriver.Chrome()
browser.get('https://bonk.io/')
delay=10#seconds
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



browser.switch_to.parent_frame()
browser.switch_to.frame('maingameframe')
try:
    myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'guestOrAccountContainer_guestButton')))
except TimeoutException:
    print("Loading took too much time!")
browser.find_element_by_id('guestOrAccountContainer_guestButton').click()


#CLICK PLAY
try:
    myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'guestOrAccountContainer_guestButton')))
except TimeoutException:
    print("Loading took too much time!")
browser.find_element_by_id('guestPlayButton').click()

try:
    myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'classic_mid_quickplay')))
except TimeoutException:
    print("Loading took too much time!")
browser.find_element_by_id('classic_mid_quickplay').click()

try:
    myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'quickPlayWindow_ClassicButton')))
except TimeoutException:
    print("Loading took too much time!")

element = browser.find_element_by_id('quickPlayWindow_ClassicButton')
browser.execute_script("arguments[0].click();", element)

print()
