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
# Running this bot at the ends of the month won't work I think 
load_dotenv()

TEST_NET = False

OSEA_URL = "https://testnets.opensea.io/" if TEST_NET else "https://opensea.io/"
COLL_URL = "https://opensea.io/assets/0x90ca8a3eb2574f937f514749ce619fdcca187d45/2787" if TEST_NET else "https://opensea.io/collection/gamblingapes"
RECOVERY = file_crypt.decrypt_file_contents("encrypted.txt")
PASS = os.getenv('PASS')
META_PATH = "/Users/colet/Library/Application Support/Google/Chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/extension_10_8_1_0.crx"

def setUpDriver():
    PATH = "/Users/colet/chromedriver"
    serv = Service(PATH)
    op = webdriver.ChromeOptions()
    op.add_argument("--no-sandbox")
    op.add_extension(META_PATH)
    prefs = {"profile.managed_default_content_settings.images": 2}
    op.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=serv, options=op)
    driver.get(OSEA_URL)
    return driver

def extract_api_info(url):
    # Returns dict with pertinent api information (name, floor price and stats)
    # "https://api.opensea.io/collection/gamblingapes"
    api_dict = {}
    req = requests.get(url).json()
    api_dict["name"] = req["collection"]["name"]
    api_dict["floor_price"] = req["collection"]["stats"]["floor_price"]
    api_dict["stats"] = req["collection"]["stats"]
    return api_dict

def date_data():
    # should return both a string to search for and a day number
    month_dict = {1:("Jan", 31), 2:("Feb", 28), 3:("Mar", 31) ,4:("Apr", 30), 5:("May",31), 
    6:("Jun",30), 7:("Jul",31), 8:("Aug",31), 9:("Sep",30), 10:("Oct", 31), 11:("Nov", 30), 12:("Dec", 31)}
    today = datetime.now()
    day = today.strftime("%d")
    hour = today.strftime("%H")
    minute = today.strftime("%S")
    month = today.strftime('%m')
    time_condition = int(hour) == 23 and int(minute) > 30
    month_condition = day == month_dict[int(month)][1]
    ### This is only worth doing if you acutally implment the clicking of the next area into the next month
    if time_condition and month_condition:
        day = 1
        month = str(int(month) + 1)
    elif time_condition:
        day = str(int(day) + 1)
    date_str = f"{month_dict[int(month)][0]} {day}"
    return day, date_str

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
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/ul/div[2]/li/button/i').click()
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

def search_bid(keyword, xpath):
    # function used to scroll through searched apes in order to find correct one (not all apes are loaded at start -- scrolling loads them)
    pass

def place_bid(driver, osea, metamask_window):
    # function that from a collection's homepage, searches a number, clicks on correct nft, makes a bid lasting 1 day and signs the transaction
    try:
        keyword = str(randint(1000,7777)) # just at 1000 for now. will need to implement code that handles number < 1000 (by scrolling and retrying on fails)
        
        # collection search bar
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div[3]/div/div/div/div[3]/div[1]/div[1]/input'))
        )
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        # find searched image
        # images = driver.find_elements(By.TAG_NAME, 'img')
        alt_str = "Gambling Ape #" + keyword
        """ for image in images:
            if image.get_attribute('alt') == alt_str:
                image.click()
                break """
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//img[@alt="{alt_str}"]'))
        ).click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Make offer"]'))
        ).click()
        # Get floor price
        api_info = extract_api_info("https://api.opensea.io/collection/gamblingapes")
        amount_bar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Amount"]'))
        )
        # send bid price
        amount_bar.send_keys(str(round(api_info["floor_price"] * 0.8, 3)))
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.XPATH, '//input[@value="7 days"]')).click()
        # click on custom date
        actions.move_by_offset(0, 225).click().perform()

        day, date_str = date_data()
        driver.find_element(By.XPATH, f'//div[contains(text(),"{date_str}, 2022")]').click()
        
        # find button for next day (to make offer time 1 day)
        day_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//button[text()="{str(int(day) + 1)}"]'))
        )
        actions.move_to_element(day_element).click()
        actions.move_to_element(driver.find_element(By.XPATH, f'//*[text()="Make an offer"]')).click()
        actions.perform()

        actions.move_to_element(driver.find_element(By.XPATH, '//button[text()="Make Offer"]'))
        actions.click().perform()
        sleep(3) # wait for metamask tx window to open

        osea = driver.current_window_handle
        child_windows = driver.window_handles

        for w in child_windows:
            if w != osea and w != metamask_window:
                driver.switch_to.window(w)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Sign"]'))
        ).click()
        # This should be dynamic (where it waits for a displayed banner)
        sleep(2) # wait for bid transaction to go through 
        return True
    except:
        print('ERROR')
        return False

def main():
    driver = setUpDriver()
    driver.implicitly_wait(3)
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
    error_count = error_reset = txs = 0
    while True:
        if error_reset > 3:
            print("ERROR: Threshold error reached.")
            print("Total bids placed:", txs)
            return 
        driver.switch_to.window(osea)
        driver.get(COLL_URL)
        bid_status = place_bid(driver, osea, metamask_window)
        if not bid_status:
            error_count += 1
            if error_count > 5:
                # if failed 3 times retry in a minute
                sleep(60)
                error_count = 0
                error_reset += 1
        else:
            txs += 1
        

if __name__ == "__main__":
    main()