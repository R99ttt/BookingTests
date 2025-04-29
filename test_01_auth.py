import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string 
import random


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"


@pytest.fixture
def driver():
    options = ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service1 = Service()
    service2 = Service()

    driver1 = webdriver.Chrome(service=service1, options=options)
    driver2 = webdriver.Chrome(service=service2)

    driver2.get("https://temp-mail.org/en")
    driver1.get("https://www.booking.com/")

    yield {"driver1": driver1, "driver2": driver2}

    driver1.quit()
    driver2.quit()

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


def test_auth(driver):
    driver1 = driver["driver1"]
    driver2 = driver["driver2"]

    wait1 = WebDriverWait(driver1, 60)  
    wait2 = WebDriverWait(driver2, 60)  

    # Get temp email
    def get_temp_email(drv):
        email = drv.find_element(By.ID, "mail").get_attribute("value")
        return email if "@" in email else False


    # Wait for temp mail be detected 
    temp_email = wait2.until(get_temp_email)
    print(f"Temp Email: {temp_email}")

    time.sleep(1)

    # Remove the google pop up 
    try:    
        iframe = driver1.find_element(By.CSS_SELECTOR, "iframe[src*='accounts.google.com/gsi/iframe']")
        driver1.execute_script("""
            let iframe = arguments[0];
            iframe.parentNode.removeChild(iframe);
        """, iframe)
        print("Google One Tap iframe removed.")
    except Exception as e:
        print("Google One Tap iframe not found or could not be removed:", e)

    # Try to remove the blocking div as well
    try:
        picker_container = driver1.find_element(By.ID, "credential_picker_container")
        driver1.execute_script("arguments[0].remove();", picker_container)
        print("Credential Picker container removed.")
    except Exception as e:
        print("Credential Picker container not found or could not be removed:", e)


    # Click Sign In
    sign_in = wait1.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Sign in']")))
    sign_in.click()

    wait1.until(EC.url_contains("https://account.booking.com/sign-in"))

    # Enter email
    wait1.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(temp_email)
    wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

    # Optional manual CAPTCHA bypass
    # input("🧩 Solve CAPTCHA if visible and press Enter...")

    # Wait for OTP email and extract code
    otp_element = wait2.until(EC.presence_of_element_located((
        By.XPATH, "//*[@id='tm-body']/main/div[1]/div/div[2]/div[2]/div/div[1]/div/div[4]/ul/li[2]/div[2]/span/a"
    )))
    otp = otp_element.text[14:20]

    # Check if OTP received 
    assert otp and len(otp) == 6, f"❌ OTP not valid or received: '{otp}'"

    # Enter OTP code
    otp_inputs = wait1.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[name^='code_']")))
    for i in range(len(otp)):
        otp_inputs[i].send_keys(otp[i])

    print(f"📧 Temp Email: {temp_email}")
    print(f"🔐 OTP Code: {otp}")

    # Submit OTP
    wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

    # Wait for login success
    wait1.until(EC.url_contains("auth_success=1"))

    assert driver1.current_url.startswith("https://www.booking.com/?auth_success=1"), \
        f"❌ Login failed: Unexpected URL {driver1.current_url}"




def test_auth_otp_error(booking_driver):
    wait1 = WebDriverWait(booking_driver, 20)
    
    sign_in_button = wait1.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Sign in']")))
    sign_in_button.click()

    username_field = wait1.until(EC.presence_of_element_located((By.ID, "username")))
    username_field.send_keys("test@gmail.com")

    submit_button = wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    submit_button.click()

    time.sleep(10)

    # Try entering wrong OTPs three times 
    for _ in range(3):  
        otp_inputs = wait1.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[name^='code_']")))

        wrong_otp = ''.join(random.choices(string.digits, k=6))

        for i in range(6):
            otp_inputs[i].clear()
            otp_inputs[i].send_keys(wrong_otp[i])

        otp_submit = wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        otp_submit.click()
        time.sleep(2)

    try:
        error_message = wait1.until(EC.presence_of_element_located((By.XPATH, "//span[@class='error-block']")))
        assert "Too many failed attempts" in error_message.text
        print("❗ Error message found:", error_message.text)
    except:
        print("❌ Error message not found.")



def test_auth_empty(booking_driver):
    wait = WebDriverWait(booking_driver, 20)

    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Sign in']")))
    sign_in_button.click()
    
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    submit_button.click()

    error_message = wait.until(EC.presence_of_element_located((By.ID, "username-note")))

    assert error_message.is_displayed()
    assert "Enter your email address" in error_message.text
