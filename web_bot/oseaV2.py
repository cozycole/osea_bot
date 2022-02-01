import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from random import randint
from datetime import datetime
import requests 
import file_crypt
from sqlitedict import SqliteDict # database
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import undetected_chromedriver as uc
""" chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--load-extension=/Users/colet/metamask-chrome-10.8.2")
driver = uc.Chrome(version=96, options=chrome_options, use_subprocess=True)
driver.get('https://opensea.io/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/5790') """
LOGGER.setLevel(logging.INFO)
os.remove("info.log")
logging.basicConfig(filename='info.log', level=logging.INFO)

load_dotenv()

TEST_NET = False

OSEA_URL = "https://opensea.io/"
COLL_URL = "https://opensea.io/collection/lazy-lions"
RECOVERY = file_crypt.decrypt_file_contents("encrypted.txt")
PASS = os.getenv('PASS')
META_PATH = "/Users/colet/Library/Application Support/Google/Chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/extension_10_8_1_0.crx"
BID_DB = SqliteDict('./bid_db.sqlite', autocommit=True)
API_DB = SqliteDict('./api_db.sqlite', autocommit=True)

def setUpDriver():
    PATH = "/Users/colet/chromedriver"
    serv = Service(PATH)
    op = webdriver.ChromeOptions()
    op.add_argument("--no-sandbox")
    op.add_argument("--window-size=1500,1080")
    op = uc.ChromeOptions()
    op.add_extension(META_PATH)
    # chrome_options.add_argument("--load-extension=/Users/colet/metamask-chrome-10.8.2")
    prefs = {"profile.managed_default_content_settings.images": 2}
    op.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=serv, options=op)
    driver.get(OSEA_URL)
    # driver = uc.Chrome(version=96, options=chrome_options, use_subprocess=True)
    driver.get(OSEA_URL)
    return driver

def extract_api_info(url, my_dict):
    # Returns dict with pertinent api information (name, floor price and stats). Cache resets every 3 hours.
    # "https://api.opensea.io/collection/gamblingapes"
    # if an api entry is present and not stale, return what's stored else update it
    if "API_INFO" in my_dict and (datetime.now() - my_dict["API_INFO"][0]).total_seconds() < 3600:
        return my_dict["API_INFO"][1]
    else:
        api_dict = {}
        req = requests.get(url).json()
        print("SENT API INFO REQUEST")
        api_dict["name"] = req["collection"]["name"]
        api_dict["floor_price"] = req["collection"]["stats"]["floor_price"]
        api_dict["stats"] = req["collection"]["stats"]
        my_dict["API_INFO"] = (datetime.now(), api_dict)
        return api_dict

def date_data():
    # should return both a string to search for and a day number to select
    month_dict = {1:("Jan", 31), 2:("Feb", 28), 3:("Mar", 31) ,4:("Apr", 30), 5:("May",31), 
    6:("Jun",30), 7:("Jul",31), 8:("Aug",31), 9:("Sep",30), 10:("Oct", 31), 11:("Nov", 30), 12:("Dec", 31)}
    today = datetime.now()
    day = today.strftime("%d")
    hour = today.strftime("%H")
    minute = today.strftime("%M")
    month = today.strftime('%m')
    search_day = day
    time_condition = int(hour) == 23 and int(minute) >= 30
    month_condition = int(day) == month_dict[int(month)][1]
    edge_case = False
    ### This is only worth doing if you acutally implment the clicking of the next area into the next month
    print("MONTH", month, "SHOULD BE 1")
    if month_condition:
        search_day = 1
        edge_case = True
    elif month_condition and time_condition:
        month = str(int(month) + 1)
    elif time_condition:
        day = str(int(day) + 1)
        search_day = day
    date_str = f"{month_dict[int(month)][0]} {day}"
    return search_day, date_str, edge_case

def metaLogIn(driver, osea, metamask_window):
    # This function will log into metamask and then connect it with OpenSea
    # Wallet details
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Get Started"]'))
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Import wallet"]'))
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="No Thanks"]'))
    ).click()

    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].send_keys(RECOVERY)
    inputs[1].send_keys(PASS)
    inputs[2].send_keys(PASS)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.first-time-flow__terms'))
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Import"]'))
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="All Done"]'))
    ).click()

    if TEST_NET:
        # clicking through necessary buttons to activate Ropsten network
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="popover-content"]/div/div/section/header/div/button'))
        ).click()

        driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
        driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[1]/div[3]/span/a').click()
        driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/div[7]/div[2]/div/div/div[1]/div[2]/div').click()
        driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
        driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div/li[1]/span').click()
    
    driver.switch_to.window(osea)
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/ul/div[2]/li/button/i'))
        ).click()
    # Gotta do this because Osea randomizes other tags and positioning of elements.
    images = driver.find_elements(By.TAG_NAME, 'img')
    MASK_IMG = "https://testnets.opensea.io/static/images/logos/metamask-alternative.png" if TEST_NET else "https://opensea.io/static/images/logos/metamask-alternative.png"
    for image in images:
        if image.get_attribute('src') == MASK_IMG:
            image.click()
            break
    sleep(3) # previous click spawns new metamask window
    child_windows = driver.window_handles
    for w in child_windows:
        if w != osea and w != metamask_window:
            driver.switch_to.window(w)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Next"]'))
    ).click()
    driver.find_element(By.XPATH, '//button[text()="Connect"]').click()
    logging.info("Signed into Metamask")

def find_meta_window(driver, osea, metamask_window):
    window_check = 0
    while True:
        sleep(2)
        try:
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[text()="Failed to Fetch"]'))
            )
            driver.find_element(By.XPATH, '//button[text()="Make Offer"]').click()
        except:
            child_windows = driver.window_handles
            if len(child_windows) > 2:
                for w in child_windows:
                    if w != osea and w != metamask_window:
                        driver.switch_to.window(w)
                        return True      
        if window_check > 5:
            print("Can't find metamask tx prompt")
            return False
        window_check += 1

def place_bid(driver, osea, metamask_window):
    # function that from a collection's homepage, searches a number, clicks on correct nft, makes a bid lasting 1 day and signs the transaction
    error = False
    try:
        keyword = str(randint(1,10000))
        # make sure we haven't already bid on this ape
        while(keyword in BID_DB):
            keyword = str(randint(1,100))
        driver.get(f"https://opensea.io/assets/0x8943c7bac1914c9a7aba750bf2b6b09fd21037e0/{keyword}")
        sleep(randint(3,5))
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Make offer"]'))
        ).click()
        sleep(randint(2,5))
        api_info = extract_api_info("https://api.opensea.io/collection/gamblingapes", API_DB)
        amount_bar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Amount"]'))
        )
        # send bid price
        # amount_bar.send_keys(str(round(api_info["floor_price"] * 0.8, 3)))
        amount_bar.send_keys("1.62")
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.XPATH, '//input[@value="7 days"]')).click()
        # click on custom date
        actions.move_by_offset(0, 225).click().perform()

        day, date_str, edge_case = date_data()

        print(date_str)
        driver.find_element(By.XPATH, f'//div[contains(text(),"{date_str}, 2022")]').click()
        if edge_case:
            # change month
            print("EDGE CASE")
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@aria-label="Next month"]'))
            ).click()
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//button[text()="{day}"]'))
            ).click()
        else:
            # find button for next day (to make offer time 1 day)
            day_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//button[text()="{str(int(day) + 1)}"]'))
            )
            actions.move_to_element(day_element).click()
        
        actions.move_to_element(driver.find_element(By.XPATH, f'//*[text()="Make an offer"]')).click()
        actions.perform()

        actions.move_to_element(driver.find_element(By.XPATH, '//button[text()="Make Offer"]')).click()
        actions.perform()

        if find_meta_window(driver, osea, metamask_window):
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]'))
            ).click()
        
        logging.info("Offer signed")
        driver.switch_to.window(osea)
        sleep(2)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[text()="Your offer was submitted successfully!"]'))
        )
        sleep(randint(1,3))
        logging.info("Successful tx")
        BID_DB[keyword] = datetime.now() # enter successfull bid into database
        logging.info("Inputted offer into db")
    except Exception as e:
        print('ERROR:', e)
        error = True
        sleep(randint(4,7))
    finally:
        # Clean up any excess windows.
        for w in driver.window_handles:
            if w != osea and w != metamask_window:
                driver.switch_to.window(w)
                driver.close()
                print("CLOSED ERRONEOUS WINDOW")
        if error:
            return False
        return True

def clean_db(dict_db):
    # checks timestamps of each stored bid and removes if day old
    now = datetime.now()
    for key, value in dict_db.iteritems():
        duration = now - value
        if duration.total_seconds() > 86400:
            del dict_db[key]

def bid_count(dict_db):
    clean_db(BID_DB)
    out_bids = 0
    for i in enumerate(dict_db):
        out_bids += 1
    return out_bids

def toggleVPN(vpn_state):
    if vpn_state:
        os.system("osascript vpn_disconnect.scpt")
    else:
        os.system("osascript vpn_connect.scpt")
    sleep(5)
    return not vpn_state

def main():
    driver = setUpDriver()
    driver.implicitly_wait(2)
    vpn_on = False
    print("Current bids:", bid_count(BID_DB))
    osea = driver.current_window_handle
    child_windows = driver.window_handles
    metamask_window = None
    for w in child_windows:
        if (w!= osea):
            driver.switch_to.window(w)
            metamask_window = w
    # must be in the metamask window before calling
    metaLogIn(driver, osea, metamask_window)
    driver.switch_to.window(osea)
    error_count = error_reset = curr_txs = total_txs = 0
    error_time = datetime.now()
    while True:
        driver.switch_to.window(osea)
        bid_status = place_bid(driver, osea, metamask_window)
        # sleeps or ends bot based on error count
        if not bid_status:
            error_count += 1
            error_time = datetime.now()
            if error_count > 5:
                error_reset += 1
                if error_reset > 3:
                    print("ERROR: Threshold error reached.")
                    print("Total bids placed:", curr_txs)
                    return
                else:
                    sleep(60)
                    error_count = 0
        else:
            if (datetime.now() - error_time).total_seconds() > 3600:
                error_count = 0
            total_txs += 1
            curr_txs += 1
            if total_txs > 1000:
                print("Total txs sent. Ending program.")
            elif curr_txs > 50 and not vpn_on:
                print("Max curr_txs sent from residential IP. Toggling VPN.")
                vpn_on = toggleVPN(vpn_on)
                curr_txs = 0
            elif curr_txs > 100 and vpn_on:
                print("Max curr_txs sent from VPN. Toggling residential.")
                vpn_on = toggleVPN(vpn_on)
                curr_txs = 0
            
            if curr_txs % 100 == 0:
                print('"Stretching"')
                print("Oustanding bids:", bid_count(BID_DB))
                print("Transaction count:", total_txs)
                sleep(randint(500, 1000))
            elif curr_txs % 20 == 0:
                print('"Coffee Break"')
                print("Transaction count:", total_txs)
                sleep(randint(60, 120))
            
        
if __name__ == "__main__":
    main()