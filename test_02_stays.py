import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"

from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options



@pytest.fixture
def booking_driver():
    options = ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service1 = Service()
    driver = webdriver.Chrome(service=service1, options=options)

    driver.get("https://www.booking.com/")
    
    yield driver
    driver.quit()



def test_search_stays(booking_driver):
    wait = WebDriverWait(booking_driver, 20) 

    # Detect destination input and enter Paris.
    destination_input = wait.until(EC.element_to_be_clickable((By.NAME, "ss")))
    destination_input.clear()
    destination_input.send_keys("Paris")

    time.sleep(1)

    # Attempt to locate the date button and click it to open the calendar.
    try:
        date_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='searchbox-dates-container']")))
        date_button.click()
    # if the calendar is already open keep going. 
    except:
        pass
    
    # Set check-in date to 7 days from today and check-out date to 10 days from today in 'YYYY-MM-DD' format.
    checkin_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    checkout_date = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")

    # Attempt to locate the check-in date in calendar.
    checkin_date_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{checkin_date}"]')))
    checkin_date_element.click()

    # Attempt to locate the check-out date in calendar.
    checkout_date_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{checkout_date}"]')))
    checkout_date_element.click()

    time.sleep(1)

    # Locate the search button and click on it.
    search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    search_button.click()

    # Locate the header in the result page. 
    result_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h1[contains(text(),'properties found')]")
    ))

    assert "Paris" in result_element.text and "properties found" in result_element.text, \
        f"Error: The search result did not include 'Paris' or 'properties found'. The actual text is: {result_element.text}"



def test_search_long_input(booking_driver):
    wait = WebDriverWait(booking_driver, 20)

    # Step 1: Navigate to the destination input field and clear any existing text
    destination_input = wait.until(EC.element_to_be_clickable((By.NAME, "ss")))
    destination_input.clear()

    # Input a very long string (more than 1000 characters)
    long_string = "A" * 10000  # Input string with 10,000 characters
    destination_input.send_keys(long_string)
    time.sleep(1)

    # Step 2: Pick valid check-in and check-out dates
    try:
        date_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='searchbox-dates-container']")))
        date_button.click()
    except Exception as e:
        print("⚠️ Could not click the date button:", str(e))

    checkin_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    checkout_date = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")

    try:
        checkin_date_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{checkin_date}"]')))
        checkin_date_element.click()

        checkout_date_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{checkout_date}"]')))
        checkout_date_element.click()
    except Exception as e:
        print("⚠️ Could not select dates:", str(e))

    # Step 3: Submit the search form
    search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    search_button.click()
    time.sleep(5)

    # Step 4: Check for any error pages (like Error 413 or 494)
    error_header = booking_driver.find_element(By.TAG_NAME, "h1")
    error_text = error_header.text.strip()

    # Check for specific error codes (e.g., 413 or 494)
    if "413" in error_text or "494" in error_text:
        print("❌ Website crashed with error:", error_text)
        assert False, f"❌ Test Failed: Website crashed with error {error_text}. System did not handle the input properly."

    # If some other error occurs
    elif error_text:
        print("⚠️ Unexpected error shown:", error_text)
        assert False, f"⚠️ Test Failed: Unexpected error message displayed: {error_text}"



def test_search_stays_empty(booking_driver):
    wait = WebDriverWait(booking_driver, 20) 

    search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    search_button.click()

    alert_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='searchbox-alert'] div.feaba1002a")))
    time.sleep(5)
    assert "Enter a destination" in alert_element.text, f"Expected alert not found. Found: {alert_element.text}"
    print("✅ Empty search alert detected as expected.")
