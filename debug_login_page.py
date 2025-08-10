#!/usr/bin/env python3
"""
Debug the login page to understand current structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_login_page():
    """Check current login page structure"""
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("🔍 Checking Pacific Giftware login page structure...")
        
        # Try different login URLs
        login_urls = [
            "https://www.pacificgiftware.com/login",
            "https://www.pacificgiftware.com/pages/login",
            "https://www.pacificgiftware.com/account/login"
        ]
        
        for url in login_urls:
            print(f"\n📍 Testing: {url}")
            try:
                driver.get(url)
                time.sleep(3)
                
                title = driver.title
                print(f"   Title: {title}")
                
                # Check for login form elements
                print("   Looking for form elements...")
                
                # Find all input fields
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"   Found {len(inputs)} input elements:")
                
                for i, input_el in enumerate(inputs):
                    input_type = input_el.get_attribute("type")
                    input_id = input_el.get_attribute("id")
                    input_name = input_el.get_attribute("name")
                    input_placeholder = input_el.get_attribute("placeholder")
                    
                    print(f"     Input {i+1}: type='{input_type}' id='{input_id}' name='{input_name}' placeholder='{input_placeholder}'")
                
                # Look for buttons
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"   Found {len(buttons)} button elements:")
                
                for i, button in enumerate(buttons):
                    button_text = button.text
                    button_type = button.get_attribute("type")
                    print(f"     Button {i+1}: text='{button_text}' type='{button_type}'")
                
                # Check if this is the working URL
                if "not found" not in title.lower() and (inputs or "login" in title.lower()):
                    print(f"   ✓ This appears to be a valid login page")
                    return url, inputs, buttons
                else:
                    print(f"   ❌ This doesn't appear to be a login page")
                    
            except Exception as e:
                print(f"   ❌ Error accessing {url}: {str(e)}")
        
        print("\n❌ No working login page found")
        return None, None, None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login_page()