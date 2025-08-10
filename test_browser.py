#!/usr/bin/env python3
"""
Test browser functionality and Pacific Giftware website access
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_browser():
    """Test if browser can access Pacific Giftware"""
    print("Testing browser access to Pacific Giftware...")
    
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    
    # Specify paths
    chrome_options.binary_location = "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium-browser"
    chromedriver_path = "/nix/store/8zj50jw4w0hby47167kqqsaqw4mm5bkd-chromedriver-unwrapped-138.0.7204.100/bin/chromedriver"
    
    try:
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Browser started successfully")
        
        # Test basic navigation
        driver.get("https://www.pacificgiftware.com")
        print(f"✓ Loaded Pacific Giftware homepage")
        print(f"  Title: {driver.title}")
        
        # Test login page
        driver.get("https://www.pacificgiftware.com/account/login")
        print("✓ Navigated to login page")
        
        # Check for login elements
        try:
            wait = WebDriverWait(driver, 10)
            
            # Try different selectors for email field
            email_selectors = [
                "input[type='email']",
                "input[name='email']", 
                "input[id='email']",
                "input[name='customer[email]']",
                "#CustomerEmail"
            ]
            
            email_found = False
            for selector in email_selectors:
                try:
                    email_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✓ Found email field with selector: {selector}")
                    email_found = True
                    break
                except:
                    continue
            
            if not email_found:
                print("⚠ No email field found, trying different approach...")
                # Get page source to analyze
                page_source = driver.page_source
                print("Page contains 'email':", 'email' in page_source.lower())
                print("Page contains 'login':", 'login' in page_source.lower())
                print("Page contains 'password':", 'password' in page_source.lower())
        
        except Exception as e:
            print(f"⚠ Error checking login elements: {e}")
        
        # Test a product page
        try:
            driver.get("https://www.pacificgiftware.com/product/12238")
            print("✓ Navigated to product page 12238")
            print(f"  Product page title: {driver.title}")
            
            # Check if product exists
            if "not found" in driver.title.lower() or "404" in driver.title.lower():
                print("⚠ Product 12238 not found")
            else:
                print("✓ Product 12238 page loaded successfully")
                
        except Exception as e:
            print(f"⚠ Error loading product page: {e}")
        
        driver.quit()
        print("✓ Browser test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Browser test failed: {e}")
        return False

if __name__ == "__main__":
    test_browser()