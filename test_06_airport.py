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
def driver():
    options = ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service1 = Service()
    driver = webdriver.Chrome(service=service1, options=options)

    driver.get("https://www.booking.com/")
    
    yield driver
    driver.quit()


def test_airport_taxi_search_flow(driver):
    wait = WebDriverWait(driver, 20)

    # 1) Open Booking.com and click "Airport taxis"
    driver.get("https://www.booking.com")
    wait.until(EC.element_to_be_clickable((By.ID, "airport_taxis"))).click()

    # wait for the URL to include airport_taxis
    wait.until(EC.url_contains("taxi"))
    assert "taxi" in driver.current_url

    # 2) Fill in "Pick‑up" -> type "London"
    pickup = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@data-testid='taxi-autocomplete-search-box__input-pickup']"
    )))
    pickup.clear()
    pickup.send_keys("London")

    # 3) Wait for the pick‑up suggestions list, then click the first <li>
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//ul[@data-testid='taxi-autocomplete-search-drop-down__container-pickup']"
    )))
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "(//ul[@data-testid='taxi-autocomplete-search-drop-down__container-pickup']/li)[1]"
    ))).click()

    # 4) Fill in "Drop‑off" -> type "Munich"
    dropoff = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@data-testid='taxi-autocomplete-search-box__input-dropoff']"
    )))
    dropoff.clear()
    dropoff.send_keys("Munich")

    # 5) Wait for the drop‑off suggestions, then click the first <li>
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//ul[@data-testid='taxi-autocomplete-search-drop-down__container-dropoff']"
    )))
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "(//ul[@data-testid='taxi-autocomplete-search-drop-down__container-dropoff']/li)[1]"
    ))).click()

    # 6) Click the "Search" button
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[@data-testid='submit-button']"
    ))).click()

    # 7) Verify that the results container appears
    result_container = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//div[@data-testid='taxi-search-form__container']"
    )))
    assert result_container.is_displayed()

    # pause so you can see it in the browser if needed
    time.sleep(3)


def test_airport_taxi_empty_fields_show_errors(driver):
    wait = WebDriverWait(driver, 20)

    # 1) Open Booking.com and click "Airport taxis"
    driver.get("https://www.booking.com")
    wait.until(EC.element_to_be_clickable((By.ID, "airport_taxis"))).click()

    # 2) Click "Search" with both pickup & dropoff empty
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[@data-testid='submit-button']"
    ))).click()

    # 3) Wait for both error tooltips to appear
    errors = wait.until(EC.presence_of_all_elements_located((
        By.XPATH,
        "//div[@data-testid='taxi-error-tooltip']"
    )))

    # 4) Assert we see two distinct tooltips (one per field)
    assert len(errors) == 2, f"Expected 2 error tooltips, got {len(errors)}"

    # 5) (Optional) pause so you can actually see them on screen
    import time; time.sleep(3)


def test_airport_taxi_large_input_shows_errors(driver):
    wait = WebDriverWait(driver, 20)
    LARGE_INPUT = "X" * 500

    # 1) Go to Booking.com and click "Airport taxis"
    driver.get("https://www.booking.com")
    wait.until(EC.element_to_be_clickable((By.ID, "airport_taxis"))).click()

    # 2) Enter nonsense into the Pick‑up field
    pickup = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@data-testid='taxi-autocomplete-search-box__input-pickup']"
    )))
    pickup.clear()
    pickup.send_keys(LARGE_INPUT)

    # 3) Enter nonsense into the Drop‑off field
    dropoff = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//input[@data-testid='taxi-autocomplete-search-box__input-dropoff']"
    )))
    dropoff.clear()
    dropoff.send_keys(LARGE_INPUT)

    # 4) Click "Search"
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[@data-testid='submit-button']"
    ))).click()

    # 5) Wait for both error tooltips to appear
    errors = wait.until(EC.presence_of_all_elements_located((
        By.XPATH,
        "//div[@data-testid='taxi-error-tooltip']"
    )))

    # 6) Assert that two tooltips are shown (one per field)
    assert len(errors) == 2, f"Expected 2 error tooltips, got {len(errors)}"

    # pause so you can visually confirm
    import time; time.sleep(3)




