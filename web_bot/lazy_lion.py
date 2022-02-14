from distutils.log import error
import os
import typing
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from random import randint
from datetime import datetime
from dotenv import load_dotenv
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
LOGGER.setLevel(logging.ERROR)
# Need to create separate error logs for each process
suffix = str(os.getpid())
path_name = R"C:\Users\ashun\osea_bot\web_bot\error" + suffix + ".log"
if os.path.exists(path_name):
    os.remove(path_name)
logging.basicConfig(filename=f"error{suffix}.log", level=logging.ERROR)

load_dotenv()

TEST_NET = False

OSEA_URL = "https://opensea.io/"
COLL_URL = "https://opensea.io/collection/lazy-lions"
RECOVERY = file_crypt.decrypt_file_contents("encrypted.txt")
PASS = os.getenv('PASS')
META_PATH = R"C:\Users\ashun\AppData\Local\Google\Chrome\User Data\Default\Extensions\nmmhkkegccagdldgiimedpiccmgmieda\extension_10_9_0_0.crx"
BID_DB = SqliteDict('./bid_db.sqlite', autocommit=True)
API_DB = SqliteDict('./api_db.sqlite', autocommit=True)

def setUpDriver() -> webdriver.Chrome:
    PATH = R"C:\Users\ashun\Documents\chromedriver"
    serv = Service(PATH)
    op = webdriver.ChromeOptions()
    op.add_argument("--no-sandbox")
    # op.add_argument("--window-size=1920,1080")
    # op = uc.ChromeOptions()
    op.add_extension(META_PATH) 
    # chrome_options.add_argument("--load-extension=/Users/colet/metamask-chrome-10.8.2")
    prefs = {"profile.managed_default_content_settings.images": 2}
    op.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=serv, options=op)
    driver.set_window_size(1500,1080)
    driver.get(OSEA_URL)
    # driver = uc.Chrome(version=96, options=chrome_options, use_subprocess=True)
    return driver

def extract_api_info(url, my_dict):
    # Returns dict with pertinent api information (name, floor price and stats). Cache resets every 3 hours.
    # "https://api.opensea.io/collection/gamblingapes"
    # if an api entry is present and not stale, return what's stored else update it
    if "API_INFO" in my_dict and (datetime.now() - my_dict["API_INFO"][0]).total_seconds() < 900:
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
    if month_condition:
        search_day = 1
        edge_case = True
    elif month_condition and time_condition:
        month = str(int(month) + 1)
        day = str(int(day) + 1)
    elif time_condition:
        search_day = str(int(day) + 1)
    date_str = f"{month_dict[int(month)][0]} {int(day)}"
    return search_day, date_str, edge_case

def meta_login(driver, osea, metamask_window):
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
            actions = ActionChains(driver)
            actions.move_to_element(image).click().perform()
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

def find_sign_meta_window(driver, osea, metamask_window):
    window_check = 0
    sleep(2)
    while True:
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[text()="Failed to Fetch"]'))
            )
            driver.find_element(By.XPATH, '//button[text()="Make Offer"]').click()
            logging.error("FAILED TO FETCH! RECLICKED OFFER BUTTON")
        except:
            child_windows = driver.window_handles
            if len(child_windows) > 2:
                for w in child_windows:
                    if w != osea and w != metamask_window:
                        driver.switch_to.window(w)
                        try:
                            # Sometimes has a contract that needs to be signed.
                            WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Wyvern Exchange Contract")]'))
                            )
                            WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]'))
                            ).click()
                            logging.error("Wyvern Exchange Pop-Up")
                            driver.switch_to.window(osea)
                            driver.find_element(By.XPATH, '//button[text()="Make Offer"]').click()
                            continue
                        except:
                            WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]'))
                            ).click()
                            driver.switch_to.window(osea)
                            return True
        if window_check > 3:
            logging.error("Can't find metamask tx prompt")
            return False
        window_check += 1

def determine_offer(driver, URL):
    royalty_deduct = 0.935
    profit_margin = 0.1
    offer_objects = driver.find_elements(By.XPATH, "//div[@class='Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX Price--amount']")
    offers = []
    for offer in offer_objects:
        # this relies on the fact that offers for the nft are in the format x WETH (COULD BE UNRELIABLE!!)
        if "WETH" in offer.text:
            offer_val = float(offer.text.replace("WETH",""))
            offers.append(offer_val)
    api_dict = extract_api_info(URL, API_DB)
    floor = api_dict["floor_price"]
    if (len(offers) == 0):
        return round(floor * 0.8, 3)
    if (round(floor * 0.8, 3) > max(offers)):
        return round(floor * 0.8, 3)
    # the 7.5% royalties are specific to Gambling Apes
    top_offer = max(offers)
    print(f"{floor * royalty_deduct} - {top_offer + 0.001} = {(floor * royalty_deduct) - (top_offer + 0.001)} > 0.07 ??")
    if (floor * royalty_deduct) - (top_offer + 0.001) > profit_margin:
        return round(top_offer + 0.001, 4) 

def place_bid(driver, osea, metamask_window):
    # function that from a collection's homepage, searches a number, clicks on correct nft, makes a bid lasting 1 day and signs the transaction
    try:
        keyword = str(randint(1,9999))
        # make sure we haven't already bid on this ape
        while(keyword in BID_DB):
            keyword = str(randint(1,9999))
        bid_url = f"https://opensea.io/assets/0x8943c7bac1914c9a7aba750bf2b6b09fd21037e0/{keyword}"
        driver.get(bid_url)
        sleep(randint(2,4))
        offer = determine_offer(driver, "https://api.opensea.io/collection/lazy-lions")
        if not offer:
            sleep(randint(1,3))
            logging.error("NOT PROFITABLE")
            return "NOT PROFITABLE"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Make offer"]'))
        ).click()
        sleep(randint(2,4))
        amount_bar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Amount"]'))
        )
        # send bid price
        #amount_bar.send_keys(str(round(api_info["floor_price"] * 0.8, 3)))
        amount_bar.send_keys(str(offer))
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.XPATH, '//input[@value="3 days"]')).click()
        # click on custom date
        actions.move_by_offset(0, 250).click().perform()
        day, date_str, edge_case = date_data()
        date_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f'//*[contains(text(),"{date_str}, 2022")]'))
        )
        curr_date = date_element.text
        actions.move_to_element(date_element).click()
        actions.perform()
        if edge_case:
            # change month
            print("EDGE CASE")
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@aria-label="Next month"]'))
            ).click()
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//button[text()="{int(day)}"]'))
            ).click()
        input_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//input[@id="start-time"]'))
        ).click()
        input_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//input[@id="start-time"]'))
        )
        # logic to place 12 hour bids
        if "PM" in curr_date:
            input_element.send_keys(Keys.RIGHT)
            input_element.send_keys(Keys.RIGHT)
            input_element.send_keys('a')
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//button[text()="{int(day)+1}"]'))
            ).click()
        else:
            input_element.send_keys(Keys.RIGHT)
            input_element.send_keys(Keys.RIGHT)
            input_element.send_keys('p')
        
        actions.move_to_element(driver.find_element(By.XPATH, f'//*[text()="Make an offer"]')).click()
        actions.perform()

        actions.move_to_element(driver.find_element(By.XPATH, '//button[text()="Make Offer"]')).click()
        actions.perform()
        window_found = find_sign_meta_window(driver, osea, metamask_window)
        # if the signing window could not be found
        if not window_found:
            raise Exception
        driver.switch_to.window(osea)
        while True:
            try:
                WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[text()="Your offer was submitted successfully!"]'))
                )
                break
            except:
                element = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[contains(text(), "API Error 400")]'))
                )
                logging.error(element.text)
                return "CRITICAL ERROR"
        sleep(randint(1,3))
        BID_DB[keyword] = datetime.now() # enter successfull bid into database
        return True
    except Exception as e:
        print('ERROR:', e)
        logging.error(e)
        sleep(randint(4,7))
        return False
    finally:
        # Clean up any excess windows.
        for w in driver.window_handles:
            if w != osea and w != metamask_window:
                driver.switch_to.window(w)
                driver.close()
                logging.error("CLOSED ERRONEOUS WINDOW")

def clean_db(dict_db):
    # checks timestamps of each stored bid and removes if day old
    now = datetime.now()
    for key, value in dict_db.iteritems():
        duration = now - value
        if duration.total_seconds() > 86400/2:
            del dict_db[key]

def bid_count(dict_db):
    clean_db(BID_DB)
    out_bids = 0
    for i in enumerate(dict_db):
        out_bids += 1
    return out_bids

def main():
    driver = setUpDriver()
    driver.implicitly_wait(2)
    print("Current bids:", bid_count(BID_DB))
    osea = driver.current_window_handle
    child_windows = driver.window_handles
    metamask_window = None
    for w in child_windows:
        if (w!= osea):
            driver.switch_to.window(w)
            metamask_window = w
    # must be in the metamask window before calling
    meta_login(driver, osea, metamask_window)
    driver.switch_to.window(osea)
    error_count = error_reset = curr_txs = total_txs = 0
    while True:
        driver.switch_to.window(osea)
        bid_status = place_bid(driver, osea, metamask_window)
        # sleeps or ends bot based on error count
        if bid_status == "CRITICAL ERROR":
            logging.error("Critical Error detected. Shutting off bot.")
            logging.error(datetime.now().strftime("%H:%M:%S"))
            return
        elif bid_status == "NOT PROFITABLE":
            continue
        elif not bid_status:
            # 5 errors in a row causes error reset
            # 3 error resets causes 30 min hibernation
            error_count += 1
            if error_count > 4:
                error_reset += 1
                if error_reset > 2:
                    logging.error("ERROR: Error threshold reached.")
                    logging.error(f"Total bids placed: {curr_txs}")
                    logging.error("Hibernating for 30 minutes")
                    sleep(1800)
                else:
                    sleep(60)
                    error_count = 0
        else:
            error_count = 0
            total_txs += 1
            curr_txs += 1
            # if total_txs > 1000:
            #     print("Total txs sent. Ending program.")
            if curr_txs % 200 == 0:
                print('"Stretching"')
                print("Oustanding bids:", bid_count(BID_DB))
                print("Transaction count:", total_txs)
                sleep(randint(500, 1000))
            elif curr_txs % 30 == 0:
                print('"Coffee Break"')
                print("Transaction count:", total_txs)
                sleep(randint(60, 120))
            
        
if __name__ == "__main__":
    main()