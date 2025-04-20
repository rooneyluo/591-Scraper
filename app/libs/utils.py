import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time

def get_driver():
    """
    Initialize and return a Chrome WebDriver with appropriate options
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance or None if initialization fails
    """
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.javascript": 2
        })
        
        # Create the driver with a service object for better error handling
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)  # Set page load timeout to 30 seconds
        print("[Utils] WebDriver initialized successfully")
        return driver
    except WebDriverException as e:
        print(f"[Error] Failed to initialize WebDriver: {str(e)}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"[Error] Unexpected error initializing WebDriver: {str(e)}")
        traceback.print_exc()
        return None

def get_page_content(driver, url, max_retries=3):
    """
    Fetch and parse the content of a webpage
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        url (str): URL to fetch
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        BeautifulSoup: Parsed HTML content or None if fetching fails
    """
    if not driver:
        print("[Error] WebDriver is not initialized")
        return None
        
    if not url or not isinstance(url, str):
        print("[Error] Invalid URL provided")
        return None
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            print(f'[Crawler] Fetching: {url} (Attempt {retry_count + 1}/{max_retries})')
            driver.get(url)
            
            # Wait a bit for any dynamic content to load
            time.sleep(2)
            
            # Check if page loaded successfully
            if "Error" in driver.title or "404" in driver.title:
                print(f"[Warning] Page may have error: {driver.title}")
            
            html_content = driver.page_source
            if not html_content or len(html_content) < 100:
                print("[Warning] Page content seems too short, might be incomplete")
                retry_count += 1
                time.sleep(2)
                continue
                
            return BeautifulSoup(html_content, 'html.parser')
            
        except TimeoutException:
            print(f"[Error] Timeout while loading {url}")
            retry_count += 1
            time.sleep(2)
            
        except WebDriverException as e:
            print(f"[Error] WebDriver exception while fetching {url}: {str(e)}")
            retry_count += 1
            time.sleep(2)
            
        except Exception as e:
            print(f"[Error] Unexpected error fetching {url}: {str(e)}")
            traceback.print_exc()
            retry_count += 1
            time.sleep(2)
    
    print(f"[Error] Failed to fetch {url} after {max_retries} attempts")
    return None
