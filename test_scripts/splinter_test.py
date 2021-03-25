import splinter
import time
from PIL import Image
from io import StringIO
import sys

try:
    browser = splinter.Browser()
    browser.visit('https://bonk.io/')

    delay=10#seconds
    #REMOVE COKIES
    time.sleep(0.1)
    # try:
    #     myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.ID, 'sp_message_iframe_403823')))
    # except TimeoutException:
    #     print("Loading took too much time!")
    # gameframe = browser.find_element_by_id('maingameframe')
    with browser.get_iframe('sp_message_iframe_403823') as frame:
    # try:
    #     myElem = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Accept']")))
    # except TimeoutException:
    #     print("Loading took too much time!")
        frame.find_by_xpath("//button[text()='Accept']").click()


    #click login
    time.sleep(0.1)
    with browser.get_iframe('maingameframe') as frame:
        frame.find_by_id('guestOrAccountContainer_accountButton').click()
        username='DefntlyNotAbot'
        password='abc123'
        frame.find_by_id('loginwindow_username').fill(username)
        frame.find_by_id('loginwindow_password').fill(password)
        #CLICK LOGIN
        frame.find_by_id('loginwindow_submitbutton').click()

        #CLICK PLAY
        
        frame.find_by_id('classic_mid_quickplay').click()


        frame.find_by_id('quickPlayWindow_ClassicButton').click()
    


        #SAVE FRAME
        element = frame.find_by_id('gamerenderer')

        for i in range(1000):
            t = time.time()
            browser.html_snapshot(sys.path[0]+'/test_img/test_img'+str(i))
            print(time.time()-t)
except:
    browser.close()
    exit(1)
