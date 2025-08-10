#!/usr/bin/env python3
"""
Debug login page to understand the current structure
"""

import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def build_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,960")
    
    chrome_paths = [
        "/usr/bin/chromium-browser",
        "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            opts.binary_location = path
            break
    
    chromedriver_paths = [
        shutil.which("chromedriver"),
        "/usr/bin/chromedriver",
        "/nix/store/8zj50jw4w0hby47167kqqsaqw4mm5bkd-chromedriver-unwrapped-138.0.7204.100/bin/chromedriver"
    ]
    
    chromedriver_path = None
    for path in chromedriver_paths:
        if path and os.path.exists(path):
            chromedriver_path = path
            break
    
    svc = Service(chromedriver_path)
    return webdriver.Chrome(service=svc, options=opts)

def debug_login_pages():
    """Debug different login page URLs"""
    urls = [
        "https://www.pacificgiftware.com/pages/login",
        "https://www.pacificgiftware.com/account/login", 
        "https://www.pacificgiftware.com/login",
        "https://www.pacificgiftware.com/account",
        "https://www.pacificgiftware.com/customer/login"
    ]
    
    driver = build_driver()
    
    try:
        for url in urls:
            print(f"\n=== Testing URL: {url} ===")
            try:
                driver.get(url)
                time.sleep(3)
                
                print(f"Page title: {driver.title}")
                print(f"Current URL: {driver.current_url}")
                
                # Check for email inputs
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[id="email"]',
                    'input[name*="email"]',
                    '#CustomerEmail'
                ]
                
                email_found = False
                for selector in email_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✓ Email field found: {selector}")
                            email_found = True
                            break
                    except:
                        continue
                
                if not email_found:
                    print("⚠ No email field found")
                
                # Check for password inputs
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[id="password"]',
                    '#CustomerPassword'
                ]
                
                password_found = False
                for selector in password_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✓ Password field found: {selector}")
                            password_found = True
                            break
                    except:
                        continue
                
                if not password_found:
                    print("⚠ No password field found")
                
                # Check for submit buttons
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:contains("Sign In")',
                    'button:contains("Login")'
                ]
                
                submit_found = False
                for selector in submit_selectors:
                    try:
                        if ':contains(' in selector:
                            continue
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✓ Submit button found: {selector}")
                            submit_found = True
                            break
                    except:
                        continue
                
                if not submit_found:
                    print("⚠ No submit button found")
                
                # Check page source for login-related content
                page_source = driver.page_source.lower()
                keywords = ['login', 'sign in', 'email', 'password', 'customer']
                for keyword in keywords:
                    count = page_source.count(keyword)
                    print(f"'{keyword}': {count} occurrences")
                
                if email_found and password_found and submit_found:
                    print("🎉 Complete login form found!")
                    return url
                
            except Exception as e:
                print(f"Error loading {url}: {e}")
        
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    working_url = debug_login_pages()
    if working_url:
        print(f"\n✓ Working login URL: {working_url}")
    else:
        print("\n⚠ No complete login form found on any URL")