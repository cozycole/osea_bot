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
import undetected_chromedriver as uc
import threading

META_PATH = R"C:\Users\ashun\AppData\Local\Google\Chrome\User Data\Default\Extensions\nmmhkkegccagdldgiimedpiccmgmieda\extension_10_9_0_0.crx"
OSEA_URL = 'https://opensea.io/'
SECRET = True
BANNER_STATUS = [
    "Your offer was submitted successfully!",
    "Failed to fetch",
    "API Error 400"
]
os.system("break>logs\info.log")
os.system("break>logs\error.log")

info_logger = logging.getLogger(f"info")
info_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [Thread:%(thread)d] %(name)s: %(message)s')
file_handler = logging.FileHandler(f"logs/info.log")
file_handler.setFormatter(formatter)
info_logger.addHandler(file_handler)

error_logger = logging.getLogger(f"error")
error_logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s [Thread:%(thread)d] %(name)s: %(message)s')
file_handler = logging.FileHandler(f"logs/error.log")
file_handler.setFormatter(formatter)
error_logger.addHandler(file_handler)

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

def setup_secret_driver() -> webdriver.Chrome:
    print("setting up driver")
    PATH = R"C:\Users\ashun\chromedriver"
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(R"--load-extension=C:\Users\ashun\metamask-chrome-10.11.2")
    # chrome_options.add_argument("user-agent=Chrome/100.0.4896.60")
    driver = uc.Chrome(version=100, options=chrome_options, use_subprocess=True, driver_executable_path=PATH)
    sleep(5)
    driver.set_window_size(1500,1080)
    driver.get(OSEA_URL)
    return driver

def extract_api_info(url, my_dict, slug):
    # Returns dict with pertinent api information (name, floor price and stats). Cache resets every 15 minutes.
    # "https://api.opensea.io/collection/gamblingapes"
    # if an api entry is present and not stale, return what's stored else update it
    if f"API_INFO_{slug}" in my_dict and (datetime.now() - my_dict[f"API_INFO_{slug}"][0]).total_seconds() < 900:
        return my_dict[f"API_INFO_{slug}"][1]
    else:
        api_dict = {}
        req = requests.get(url).json()
        info_logger.info("SENT API INFO REQUEST")
        api_dict["name"] = req["collection"]["name"]
        api_dict["floor_price"] = req["collection"]["stats"]["floor_price"]
        api_dict["stats"] = req["collection"]["stats"]
        my_dict[f"API_INFO_{slug}"] = (datetime.now(), api_dict)
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
    time_condition = int(hour) == 23 and int(minute) >= 30 # 
    month_condition = int(day) == month_dict[int(month)][1] # last day of month?
    edge_case = False
    ### This is only worth doing if you acutally implment the clicking of the next area into the next month
    if month_condition and time_condition:
        month = str(int(month) + 1)
        day = str(1)
        search_day = 1
        edge_case = True
    elif month_condition:
        search_day = 1
        edge_case = True
    elif time_condition:
        search_day = str(int(day) + 1)
    date_str = f"{month_dict[int(month)][0]} {day.lstrip('0')}"
    return search_day, date_str, edge_case

def meta_login(driver: webdriver.Chrome, password, recovery):
    # This function will log into metamask and then connect it with OpenSea
    # Wallet details
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Get Started"]')),
        message = "meta_login: Could not find Get Started button"
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Import wallet"]')),
        message = "meta_login: Could not find Import Wallet button"
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="No Thanks"]')),
        message = "meta_login: Could not find No Thanks button"
    ).click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your Secret Recovery Phrase"]')),
        message = "meta_login: Could not find Recovery input"
    ).send_keys(recovery)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="password"]')),
        message = "meta_login: Could not find Password input"
    ).send_keys(password)
    """ sleep(500)
    try:
        inputs = driver.find_elements(By.XPATH, '//input')
        inputs[0].send_keys(recovery)
        inputs[2].send_keys(password)
    except:
        error_logger.error("meta_login: Could not input recovery and password")
        raise TimeoutError """

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="confirm-password"]')),
        message = "meta_login: Could not find element"
    ).send_keys(password)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="create-new-vault__terms-checkbox"]')),
        message = "meta_login: Could not find element"
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Import"]')),
        message = "meta_login: Could not find Import button"
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="All Done"]')),
        message = "meta_login: Could not find All Done button"
    ).click()
    info_logger.info("Signed into Metamask")

def opensea_login(driver: webdriver.Chrome, osea, metamask_window):
    driver.switch_to.window(osea)
    driver.refresh()
    sleep(2)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="account_balance_wallet"]')),
        message = "opensea_login: Could not find wallet icon"
    ).click()
    # Gotta do this because Osea randomizes other tags and positioning of elements.
    sleep(2)
    images = driver.find_elements(By.TAG_NAME, 'img')
    MASK_IMG = "https://opensea.io/static/images/logos/metamask-alternative.png"
    image_found = False
    for image in images:
        if image.get_attribute('src') == MASK_IMG:
            actions = ActionChains(driver)
            actions.move_to_element(image).click().perform()
            image_found = True
            break
    if not image_found:
        error_logger.error("opensea_login: could not find metamask image")
        raise Exception

    sleep(3) # previous click spawns new metamask window
    child_windows = driver.window_handles
    while len(child_windows) == 2:
        sleep(2)
        child_windows = driver.window_handles
    for w in child_windows:
        if w != osea and w != metamask_window:
            driver.switch_to.window(w)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Next"]')),
        message = "opensea_login: could not find Metamask pop up Next button"
    ).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Connect"]')),
        message = "opensea_login: could not find Metamask pop up Connect button"
    ).click()
    info_logger.info("Signed into Opensea")

def check_failed_fetch(driver: webdriver.Chrome):
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Failed to Fetch"]')),
        )
        error_logger.error("Failed Fetch Detected")
        driver.find_element(By.XPATH, '//button[text()="Make Offer"]').click()
        return True
    except:
        return False

def check_auth_sig(driver: webdriver.Chrome, osea, metamask):
    # every 24 hours, opensea requires you to sign an authentication 
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Authentication required"]')),
        )
        print("Authentication required found")
        sleep(2)
        child_windows = driver.window_handles
        for w in child_windows:
            if (w!= osea) and (w != metamask):
                driver.switch_to.window(w)
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]')),
        ).click()
        driver.switch_to.window(osea)
    except:
        return

def find_sign_meta_window(driver: webdriver.Chrome, osea, metamask_window):
    window_check = 0
    check_failed_fetch(driver)
    sleep(randint(1,2))
    while True:
        for i in range(2):
            sleep(2)
            not_found = True
            child_windows = driver.window_handles
            for w in child_windows:
                if w != osea and w != metamask_window:
                    not_found = False
                    driver.switch_to.window(w)
                    try:
                        WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@data-testid="signature-request-scroll-button"]')),
                            message="find_sign_meta_window: Can't find scroll button"
                        ).click()
                        sleep(1)
                        WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]')),
                            message="find_sign_meta_window: Can't find Sign button"
                        ).click()
                        driver.switch_to.window(osea)
                        return True
                    except:
                        return False
        if not_found:
            # reclick the make offer button if can't find metamask window
            sleep(5)
            driver.find_element(By.XPATH, '//button[text()="Make Offer"]').click()
            error_logger.error("offer button reclicked")
                    
        if window_check == 2:
            error_logger.error("Can't find metamask tx prompt")
            return False
        window_check += 1

def determine_offer(driver: webdriver.Chrome, URL, royalty_deduct, api_db, slug):
    profit_margin = 0.08
    offer_objects = driver.find_elements(By.XPATH, "//div[@class='Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX Price--amount']")
    offers = []
    for offer in offer_objects:
        # this relies on the fact that offers for the nft are in the format x WETH (COULD BE UNRELIABLE!!)
        if "WETH" in offer.text:
            offer_val = float(offer.text.replace("WETH",""))
            offers.append(offer_val)
    api_dict = extract_api_info(URL, api_db, slug)
    floor = api_dict["floor_price"]
    if (len(offers) == 0):
        return round(floor * 0.8, 3)
    if (round(floor * 0.8
    , 3) > max(offers)):
        return round(floor * 0.8, 3)
    top_offer = max(offers)
    info_logger.info(f"{floor * royalty_deduct} - {top_offer + 0.001} = {(floor * royalty_deduct) - (top_offer + 0.001)} > {profit_margin} is {((floor * royalty_deduct) - (top_offer + 0.001)) >= profit_margin}")
    if ((floor * royalty_deduct) - (top_offer + 0.001)) >= profit_margin:
        print("OUT BID!!")
        return round(top_offer + 0.001, 4) 

def find_status_banner(driver: webdriver.Chrome):
    # Find the banner status after signing a transaction
    #
    try:
        banner_divs = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@role="alert"]//div')),
                    #EC.presence_of_element_located((By.XPATH, '//div[@class="Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 jffCaG jYqxGr"]')),
                    message="find_status_banner: Could not find banner divs"
        )
        for div in banner_divs:
            for status in BANNER_STATUS:
                if status in div.text:
                    return div.text
    except:
        return False

def handle_status(driver: webdriver.Chrome, osea, metamask, banner_text, fetch_failed):
    # fetch_failed used for the recursive call
    if banner_text:
        # if successful log into db
        if "success" in banner_text:
            return True
        # if it has failed to fetch, we will try once again. If it fails again, we will return an error
        elif "fetch" in banner_text and not fetch_failed:
            sleep(randint(2,4))
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[text()="Make offer"]')),
                message="place_bid: Could not find Make Offer button (during failed to fetch handle)"
            ).click()
            window = find_sign_meta_window(driver, osea, metamask)
            if window:
                status = find_status_banner(driver)
                return handle_status(driver, osea, metamask, status, True)
        elif "fetch" in banner_text and fetch_failed:
            return False
        else:
            error_logger.error(banner_text)
            return "API ERROR"
    else:
        error_logger.error("Could not find banner text")
    return False

def bid_date_input(driver: webdriver.Chrome, date, day, bid_dur, edge_case):
    # Date in the form: Feb 21, 2022 11:07 AM
    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//input[@id="start-time"]')),
                message="bid_date_input: Could not find start time"
        ).click()
    input_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//input[@id="start-time"]')),
            message="bid_date_input: Could not find start time (2nd)"
    )
    date_elements = date.split()
    time = date_elements[3].split(':') # hour, mintues
    bid_time = ((int(time[0]) % 12) + bid_dur) % 24
    # print(f"12 - {(int(time[0]) % 12)} = {(12 - (int(time[0]) % 12))} <= {bid_dur}")
    # if bid time leaks from am to pm or vice versa
    if (12 - (int(time[0]) % 12)) <= bid_dur:
        input_element.send_keys(str(bid_time))
        input_element.send_keys(Keys.RIGHT)
        if "PM" in date and edge_case:
            # if bid time leaks into a new month
            info_logger.info("EDGE CASE")
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@aria-label="Next month"]')),
                message="place_bid: Could not find Next Month button (edge case)"
            ).click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f'//button[text()="{int(day)}"]')),
                message="place_bid: Could not find day button (edge case)"
            ).click()
        elif "PM" in date:
                input_element.send_keys('a')
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f'//button[text()="{int(day)+1}"]')),
                    message="bid_date_input: Could not find day button"
                ).click()
        else:
            input_element.send_keys('p')
    else:
        input_element.send_keys(str(bid_time))

def place_bid(driver: webdriver.Chrome, osea, metamask_window, slug, royalties, address, bid_dur, bid_lock: threading.Lock):
    api_db = SqliteDict('./api_db.sqlite', autocommit=True)
    bid_db = SqliteDict(f'./bid_db.sqlite', autocommit=True)
    try:
        list_number = randint(1,10000)
        keyword = f"{slug}:{list_number}"
        while(keyword in bid_db or (list_number in api_db[f"{slug}_rare_list"])):
            list_number = randint(1,10000)
            keyword = f"{slug}:{list_number}"
        bid_url = f"https://opensea.io/assets/{address}/{list_number}"
        driver.get(bid_url)
        sleep(randint(2,3))
        offer = determine_offer(driver, f"https://api.opensea.io/collection/{slug}", royalties, api_db, slug)
        if not offer:
            sleep(randint(3,5))
            error_logger.error("NOT PROFITABLE")
            return "NOT PROFITABLE"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Make offer"]')),
            message="place_bid: Could not find Make Offer button"
        ).click()
        check_auth_sig(driver, osea, metamask_window)
        
        sleep(randint(1,3))
        amount_bar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Amount"]')),
            message="place_bid: Could not find Amount input"
        )
        amount_bar.send_keys(str(offer))
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.XPATH, '//input[@value="3 days"]')).click()
        # click on custom date
        actions.move_by_offset(0, 250).click().perform()
        day, date_str, edge_case = date_data()
        # print(date_str)
        date_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f'//*[contains(text(),"{date_str}, 2022")]')),
                message="place_bid: Could not find text date input"
        )
        curr_date = date_element.text
        # info_logger.info(f"DATE ELEMENT:{curr_date}")
        actions.move_to_element(date_element).click()
        actions.perform()
        bid_date_input(driver, curr_date, day, bid_dur, edge_case)
        with bid_lock:
            actions.move_to_element(driver.find_element(By.XPATH, f'//*[text()="Make an offer"]')).click()
            actions.perform()
            actions.move_to_element(driver.find_element(By.XPATH, '//button[text()="Make Offer"]')).click()
            actions.perform()

            window_found = find_sign_meta_window(driver, osea, metamask_window)
            driver.switch_to.window(osea)
            banner_text = find_status_banner(driver)
            status = handle_status(driver, osea, metamask_window, banner_text, False)
        # if the signing window could not be found, we try again one time
        if status is True:
            sleep(randint(2,3))
            bid_db[keyword] = datetime.now() # enter successfull bid into database
            return True
        elif status == "API ERROR":
            return "API ERROR"
        else:
            return False
    except Exception as e:
        error_logger.error(f"ERROR: {e}")
        sleep(randint(4,7))
        return False
    finally:
        # Clean up any excess windows in case of an error.
        for w in driver.window_handles:
            if w != osea and w != metamask_window:
                driver.switch_to.window(w)
                driver.close()
                error_logger.error("CLOSED ERRONEOUS WINDOW")

def clean_db(dict_db, bid_dur):
    # checks timestamps of each stored bid and removes if day old
    now = datetime.now()
    for key, value in dict_db.iteritems():
        duration = now - value
        if duration.total_seconds() > bid_dur*60*60:
            del dict_db[key]

def bid_count(dict_db, bid_dur):
    clean_db(dict_db, bid_dur)
    out_bids = 0
    for i in enumerate(dict_db):
        out_bids += 1
    return out_bids

def main(slug, royalties, address, bid_dur, bid_lock):
    # Needed to create separate error logs for each thread
    suffix = threading.get_ident()
    info_logger.info(f"NEW THREAD STARTED:{suffix}")
    bid_db = SqliteDict(f'./bid_db.sqlite', autocommit=True)

    load_dotenv()
    recovery = file_crypt.decrypt_file_contents("encrypted.txt")
    password = os.getenv('PASS')
    driver = setup_secret_driver() if SECRET else setUpDriver()
    sleep(5)
    info_logger.info(f"Current bids: {bid_count(bid_db, bid_dur)}")
    osea = driver.current_window_handle
    child_windows = driver.window_handles
    metamask_window = None
    for w in child_windows:
        if (w!= osea):
            driver.switch_to.window(w)
            metamask_window = w
    # must be in the metamask window before calling
    meta_login(driver, password, recovery)
    driver.switch_to.window(osea)
    opensea_login(driver, osea, metamask_window)
    error_count = error_reset = curr_txs = no_profit = total_txs = 0
    while True:
        driver.switch_to.window(osea)
        bid_status = place_bid(driver, osea, metamask_window, slug, royalties, address, bid_dur, bid_lock)
        # sleeps or ends bot based on error count
        if bid_status == "API ERROR":
            error_logger.error("Critical Error detected. Shutting off bot for an hour.")
            error_logger.error(datetime.now().strftime("%H:%M:%S"))
            sleep(3600)
        elif bid_status == "NOT PROFITABLE":
            no_profit += 1
            if no_profit > 10:
                sleep(3600)
            no_profit = 0
            continue
        elif not bid_status:
            # 5 errors in a row causes error reset
            # 3 error resets causes 20 min hibernation
            error_count += 1
            if error_count > 4:
                error_reset += 1
                if error_reset > 2:
                    error_logger.error("ERROR: Error threshold reached.")
                    error_logger.error(f"Total bids placed: {curr_txs}")
                    error_logger.error("Hibernating for 20 minutes")
                    sleep(1200)
                    error_reset = 0
                    error_count = 0
                else:
                    sleep(60)
                    error_count = 0
        else:
            error_count = 0
            no_profit = 0
            total_txs += 1
            curr_txs += 1
            if curr_txs % 200 == 0:
                info_logger.info(f'"Stretching" {datetime.now()}')
                info_logger.info(f"Oustanding bids: {bid_count(bid_db, bid_dur)}")
                info_logger.info(f"Transaction count:{total_txs}")
                sleep(randint(500, 1000))
            elif curr_txs % 40 == 0:
                info_logger.info(f'"Coffee Break" {datetime.now()}')
                info_logger.info(f"Transaction count:{total_txs}")
                sleep(randint(60, 120))
