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
def driver():
    options = ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service1 = Service()
    driver = webdriver.Chrome(service=service1, options=options)

    driver.get("https://www.booking.com/")
    
    yield driver
    driver.quit()


def test_car_rental_search_flow(driver):
    wait = WebDriverWait(driver, 40)

    # 1) Go to Booking.com
    driver.get("https://www.booking.com")

    # 2) Click “Car rentals”
    wait.until(EC.element_to_be_clickable((By.ID, "cars"))).click()

    # Check the car rental button
    wait.until(EC.url_contains("/cars"))
    assert "/cars" in driver.current_url

    # 3) Enter “London” into the pickup-location field
    pickup = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@name='pickup-location' and contains(@class,'SearchBoxFieldAutocomplete_input')]"
    )))
    pickup.clear()
    pickup.send_keys("London")

    # 4) Wait for the dropdown listbox
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='listbox']")))

    # 5) Click the first suggestion:
    #    - select the first <div> child under role="listbox"
    #    - then click its <button>
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "(//div[@role='listbox']/div)[1]//button"
    ))).click()

    # 6) Click “Search”
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//div[contains(@class,'SearchBoxFramePrivate_submit')]//button[@type='submit']"
    ))).click()

    # 7) Verify the results header appears (any <h1> whose class starts with "SM_")
    result_header = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//h1[starts-with(@class,'SM_')]"
    )))
    assert result_header.is_displayed()

def test_car_rental_search_without_pickup_location(driver):
    wait = WebDriverWait(driver, 15)

    # 1) Go to Booking.com
    driver.get("https://www.booking.com/?lang=en-gb")

    # 2) Click "Car rentals"
    wait.until(EC.element_to_be_clickable((By.ID, "cars"))).click()

    # 3) Click "Search" without entering pickup location
    wait.until(EC.element_to_be_clickable((
        By.XPATH, "//div[contains(@class,'SearchBoxFramePrivate_submit')]//button[@type='submit']"
    ))).click()

    # 4) Wait for ANY error message element to appear
    error_element = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//span[contains(@class,'SearchBoxFrameItem_error')]"
    )))

    # — pause so you can see the error message on screen —
    time.sleep(5)

    # 5) Assert it’s visible
    assert error_element.is_displayed()

def test_car_rental_large_input_no_text_matching(driver):
    wait = WebDriverWait(driver, 20)
    LARGE_INPUT = "X" * 500

    # 1) Go to Booking.com -> Car rentals
    driver.get("https://www.booking.com/?lang=en-gb")
    wait.until(EC.element_to_be_clickable((By.ID, "cars"))).click()

    # 2) Type the huge string
    pickup = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@name='pickup-location' and contains(@class,'SearchBoxFieldAutocomplete_input')]"
    )))
    pickup.clear()
    pickup.send_keys(LARGE_INPUT)

    # 3) Wait for the dropdown “No Results” container by class only
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//div[@role='listbox']//div[contains(@class,'LPCM_f06d4876')]"
    )))

    # 4) Click Search
    wait.until(EC.element_to_be_clickable((
        By.XPATH, "//span[contains(@class,'LPCM_b7bff305')]"
    ))).click()

    # 5) Assert the pick‑up‑location error appears
    error_el = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//span[contains(@class,'SearchBoxFrameItem_error')]"
    )))
    time.sleep(3)  
    assert error_el.is_displayed()
