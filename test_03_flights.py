import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta

# Custom User-Agent for stealth
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"


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

def test_flight_search(booking_driver):
    driver = booking_driver
    wait = WebDriverWait(driver, 20)

    # 1) Navigate & open Flights tab
    driver.get("https://booking.kayak.com/")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//a[contains(@class,'UIM7-product') and normalize-space(.)='Flights']")
    )).click()

    # 2) Clear any existing origin
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//div[contains(@class,'c_neb-item-close')]//div[@role='button']")
    )).click()

    # 3) Enter origin → select first suggestion
    origin = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//input[@aria-label='Flight origin input']")
    ))
    origin.clear()
    origin.send_keys("Tel Aviv")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "(//li[@role='option'])[1]")
    )).click()

    # 4) Enter destination → select first suggestion
    dest = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//input[@data-test-destination]")
    ))
    dest.clear()
    dest.send_keys("Paris")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "(//li[@role='option'])[1]")
    )).click()

    # 5) Compute dynamic dates (7 days out, 2-day return)
    today          = date.today()
    depart_date    = today + timedelta(days=7)
    return_date    = depart_date + timedelta(days=2)
    # labels must match the beginning of the aria-label on each date-button
    depart_label   = depart_date.strftime("%B") + " " + str(depart_date.day) + ", " + str(depart_date.year)
    return_label   = return_date.strftime("%B") + " " + str(return_date.day) + ", " + str(return_date.year)

    # 6) Open the Departure calendar
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//div[@aria-label='Departure']")
    )).click()
    # 7) Click the computed departure date
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         f"//td[@role='gridcell']//div[@role='button' and contains(@aria-label, '{depart_label}')]")
    )).click()

    # 8) Open the Return calendar
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//div[@aria-label='Return']")
    )).click()
    # 9) Click the computed return date
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         f"//td[@role='gridcell']//div[@role='button' and contains(@aria-label, '{return_label}')]")
    )).click()

    #10) Close the nav bar in small screen 
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//h2[@class='AQWr-mod-margin-bottom-xlarge c0qPo']"
        )
    )).click()

    # 11) Click Search
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//button[@aria-label='Search']")
    )).click()

    # 12) Wait for the results container (stable, non-changing ID)
    results = wait.until(EC.visibility_of_element_located(
        (By.XPATH,
         "//div[@id='flight-results-list-wrapper']")
    ))
    time.sleep(3)
    assert results.is_displayed(), "Flight results did not load"