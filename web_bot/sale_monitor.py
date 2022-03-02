import requests
import json
import os
from sqlitedict import SqliteDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import file_crypt
from time import sleep
import typing
##########################################################################################
# Polls Etherscan every 30 seconds for new ERC721 transaction for our @
# If new sale detected, will convert WETH to ETH (maybe better way to detect a dump)
# start block inclusive so after seeing new transactions, set new start block to last + 1
##########################################################################################

def poll_etherscan(address_to_poll):
    """
    Returns 
    if txn exists:
        a list of the inbound transactions within the last block number in the API database
    else:
        False
    """
    api_db = SqliteDict('./api_db.sqlite', autocommit=True)
    block_num = api_db["POLLING_BLOCK"]
    # print(f"Polling for {address_to_poll} starting at block number {block_num} ")
    URL = f"https://api.etherscan.io/api?module=account&action=tokennfttx&address={address_to_poll}&startblock={block_num}&endblock=999999999&sort=asc&apikey=NF59JSQ23GUIN9CS6TR1N3ME42PXIH5B8T"
    try:
        response = requests.get(URL).json()
    except:
        print("ETHERSCAN ERROR")
        return False
    if response["message"] == "No transactions found":
        return False
    # Check now to see if the transactions are IN or OUT (is to == MY_ADDRESS)
    in_txns = []
    for txn in response["result"]:
        if txn["to"] == address_to_poll:
            in_txns.append(txn)
    new_block_num = response["result"][-1]["blockNumber"]
    api_db["POLLING_BLOCK"] = int(new_block_num) + 1
    # calling function should check if out_txns is empty or not
    # empty -> no outbound transactions, continue polling
    # not empty -> we got an nft 
    return in_txns

def convert_to_ETH(driver: webdriver, meta_window):
    """
    Converts WETH balance back to ETH to avoid a NFT dump on the wallet
    Opens up metamask and swaps WETH to ETH
    """
    window_found = False
    for window in driver.window_handles:
        if window == meta_window:
            driver.switch_to.window(window)
            window_found = True
    if not window_found:
        return False
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@class="fas fa-times popover-header__button"]'))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Swap"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//img[@src="./images/black-eth-logo.svg"]'))
    ).click()
    sleep(2)
    """ WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search for a token"]'))
    ).click()
    search_bar.send_keys("WETH")
    search_bar.send_keys(Keys.ENTER) """
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Wrapped Ether"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Max"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Select a token"]'))
    ).click()
    """ search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search for a token"]'))
    ).click()
    search_bar.send_keys("ETH")
    search_bar.send_keys(Keys.ENTER) """
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Ether"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[text()="Review Swap"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Swap"]'))
    ).click()

# RECOVERY = file_crypt.decrypt_file_contents("encrypted.txt")
# PASS = os.getenv('PASS')
# META_PATH = os.getenv('META_PATH')

# PATH = R"C:\Users\ashun\Documents\chromedriver"
# serv = Service(PATH)
# op = webdriver.ChromeOptions()
# op.add_argument("--no-sandbox")
# op.add_argument("--window-size=1500,1080")
# op.add_extension(R"C:\Users\ashun\AppData\Local\Google\Chrome\User Data\Default\Extensions\nmmhkkegccagdldgiimedpiccmgmieda\extension_10_9_0_0.crx"
# )
# driver = webdriver.Chrome(service=serv, options=op)
# base = driver.current_window_handle

# change = False
# while not change:
#     for w in driver.window_handles:
#         if w != base:
#             driver.switch_to.window(w)
#             change = True
#             print("checking")

# cc.meta_login(driver, None, driver.current_window_handle)
# convert_to_ETH(driver, driver.current_window_handle) 
