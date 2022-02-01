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
import undetected_chromedriver as uc

RECOVERY = file_crypt.decrypt_file_contents("encrypted.txt")
PASS = os.getenv('PASS')
OSEA_URL = "https://opensea.io/collection/gamblingapes"
COLL_URL = "https://opensea.io/collection/gamblingapes"
META_PATH = "/Users/colet/Library/Application Support/Google/Chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/extension_10_8_1_0.crx"
BID_DB = SqliteDict('./bid_db.sqlite', autocommit=True)


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

    driver.switch_to.window(osea)
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/ul/div[2]/li/button/i'))
        ).click()
    # Gotta do this because Osea randomizes other tags and positioning of elements.
    images = driver.find_elements(By.TAG_NAME, 'img')
    MASK_IMG = "https://opensea.io/static/images/logos/metamask-alternative.png"
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

def url_crawl(driver):
    driver.get(COLL_URL)
    
    pass

def main():
    pass