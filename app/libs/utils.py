from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.javascript": 2
    })
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def get_page_content(driver, url):
    driver.get(url)
    print('[Crawler] Fetching:', url)
    return BeautifulSoup(driver.page_source, 'html.parser')