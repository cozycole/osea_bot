from time import sleep
import undetected_chromedriver as uc
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--load-extension=/Users/colet/metamask-chrome-10.8.2")
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
driver = uc.Chrome(version=96, options=chrome_options, use_subprocess=True)
driver.get('https://opensea.io/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/5790')

sleep(20)
