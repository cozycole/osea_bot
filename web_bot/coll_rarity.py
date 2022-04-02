from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import bidder
from time import sleep

"""
This script gets a list of the numbers of the top 10% rarest nfts in a collection from raritytools
The list is useful for avoiding this top percentage when placing bids, since it is unlikely
a holder will sell a rare one below floor

input the rarity url, and collection count -> list of ints
"""
def get_rarity_list(rarity_url, coll_count):
    rarity_url = "https://rarity.tools/lazy-lions"
    coll_count = 10000
    top_percent = coll_count * 0.1
    driver = bidder.setup_secret_driver()
    driver.get(rarity_url)
    sleep(10)
    rarity_list = []
    # there are 50 per page
    iterations = top_percent//50
    for i in range(int(iterations)):
        a_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@target="_blank"]')),
            #EC.presence_of_element_located((By.XPATH, '//div[@class="Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 jffCaG jYqxGr"]')),
            message="find_status_banner: Could not find banner divs"
        )
        for element in a_elements:
            if re.match("#[0-9]+", element.text):
                rarity_list.append(int(element.text[1:]))

        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@class="select-none smallBtn"]')),
            #EC.presence_of_element_located((By.XPATH, '//div[@class="Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 jffCaG jYqxGr"]')),
            message="find_status_banner: Could not find banner divs"
        )
        for button in next_button:
            if "Next" in button.text :
                button.click()
                break
        sleep(5)

    print(rarity_list)
    print("List length:", len(rarity_list))
    return(rarity_list)