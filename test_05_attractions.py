import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Custom User-Agent for stealth
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


def test_attractions_search(booking_driver):
    wait = WebDriverWait(booking_driver, 20) 

    # Locate the experience button and click on it.
    experiences_link = wait.until(EC.element_to_be_clickable((By.ID, "attractions")))
    experiences_link.click()    

    # Locate the text in the experience page 
    heading_element = WebDriverWait(booking_driver, 20).until(
        EC.presence_of_element_located((
            By.XPATH, "//h1[contains(text(), 'Attractions, activities, and experiences')]"
        ))
    )

    assert "Attractions, activities, and experiences" in heading_element.text, \
        f"Error: Expected heading not found. Got: {heading_element.text}"

    # Locate the destination input and enter Paris. 
    destination_input = wait.until(EC.element_to_be_clickable((By.NAME, "query")))
    destination_input.clear()
    destination_input.send_keys("Paris")

    time.sleep(3)

    # Locate the search button and check if it clickable then click on it. 
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='search-button']")))
    assert search_button.is_enabled(), "Error: Search button is not enabled or clickable."
    search_button.click()

    time.sleep(2)
    search_button.click()

    # Locate specific text on the result page (currently hard-coded for testing or fixed scenarios)
    result_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h1[contains(text(),'Paris attractions')]")
    ))

    assert "Paris" in result_element.text and "attraction" in result_element.text, \
        f"Unexpected result heading: {result_element.text}"
