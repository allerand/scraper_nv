import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os


def is_logged_in(driver):
    """
    Check if already logged into Gmail
    """
    try:
        driver.get("https://mail.google.com")
        time.sleep(3)
        
        indicators = [
            "//div[contains(text(), 'Compose')]",    # English
            "//div[contains(text(), 'Redactar')]",   # Spanish
            "//div[contains(@role, 'main')]"         # General Gmail UI
        ]
        
        for indicator in indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    print("[INFO] Already logged into Gmail")
                    return True
            except:
                continue
                
        print("[INFO] No active Gmail session detected")
        return False
    except Exception as e:
        print(f"[WARNING] Error checking login status: {e}")
        return False

def handle_passkey_prompt(driver):
    """
    Handle passkey dialog if it appears
    """
    try:
        time.sleep(3)
        
        dialog_indicators = [
            "//h1[contains(text(), 'Simplify your sign-in')]",
            "//h1[contains(text(), 'Simplifica el acceso')]",
            "//span[text()='Not now']",
            "//span[text()='Ahora no']"
        ]
        
        dialog_present = False
        for indicator in dialog_indicators:
            try:
                if driver.find_element(By.XPATH, indicator).is_displayed():
                    dialog_present = True
                    break
            except:
                continue
        
        if not dialog_present:
            return True
            
        print("[INFO] Passkey dialog detected, attempting to skip...")
        
        skip_button_texts = ["Not now", "Ahora no"]
        for text in skip_button_texts:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{text}']"))
                )
                button.click()
                time.sleep(2)
                return True
            except:
                continue
                
        return True
        
    except Exception as e:
        print(f"[WARNING] Error handling passkey dialog: {e}")
        return True

def login_to_gmail(driver):
    """
    Log into Gmail or verify existing session
    """
    try:
        if is_logged_in(driver):
            return True
            
        print("[INFO] Starting Gmail login process...")
        
        driver.get("https://accounts.google.com/")
        
        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_input.send_keys(os.getenv("GMAIL_EMAIL"))
        email_input.send_keys(Keys.RETURN)
        print("[INFO] Email entered")

        password_selectors = [
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
            (By.XPATH, "//input[@type='password']")
        ]

        password_input = None
        for selector_type, selector_value in password_selectors:
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                if password_input:
                    break
            except:
                continue

        if not password_input:
            raise Exception("Password field not found")

        time.sleep(2)
        password_input.clear()
        password_input.send_keys(os.getenv("GMAIL_PASSWORD"))
        time.sleep(1)
        password_input.send_keys(Keys.RETURN)
        print("[INFO] Password entered")

        handle_passkey_prompt(driver)
        
        if is_logged_in(driver):
            print("[INFO] Successfully logged into Gmail")
            return True
        else:
            raise Exception("Could not verify successful login")
        
    except Exception as e:
        print(f"[ERROR] Gmail login failed: {e}")
        raise