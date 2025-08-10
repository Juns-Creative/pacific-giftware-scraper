#!/usr/bin/env python3
"""
Final Pacific Giftware Scraper - Optimized Version
Gets product names, case quantities, and attempts pricing
"""

import os
import sys
import csv
import time
import shutil
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

LOGIN_URLS = [
    "https://www.pacificgiftware.com/pages/login"
]

def _first_present(driver, selectors, timeout=15):
    end = time.time() + timeout
    last_err = None
    while time.time() < end:
        for how, sel in selectors:
            try:
                return driver.find_element(how, sel)
            except NoSuchElementException as e:
                last_err = e
        time.sleep(0.25)
    raise last_err or TimeoutException("Elements not found")

def login(driver, email=None, password=None, wait=20):
    email = email or os.environ.get("PACIFIC_EMAIL")
    password = password or os.environ.get("PACIFIC_PASSWORD")
    if not email or not password:
        raise RuntimeError("PACIFIC_EMAIL / PACIFIC_PASSWORD not set")

    form_found = False
    for url in LOGIN_URLS:
        driver.get(url)
        try:
            # Wait for Material-UI login form to load
            WebDriverWait(driver, 12).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, 'mui-2')),  # Email field
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
                )
            )
            form_found = True
            break
        except TimeoutException:
            continue
    if not form_found:
        raise TimeoutException("Login form not found on any login URL")

    # Find email field (Material-UI uses text type, not email type)
    email_el = _first_present(driver, [
        (By.ID, 'mui-2'),  # Specific Material-UI ID
        (By.CSS_SELECTOR, 'input[type="text"]'),
        (By.CSS_SELECTOR, 'input[type="email"]'),
        (By.CSS_SELECTOR, 'input[name="email"]'),
        (By.ID, 'email'),
    ], timeout=10)

    # Find password field
    pw_el = _first_present(driver, [
        (By.ID, 'mui-3'),  # Specific Material-UI ID  
        (By.CSS_SELECTOR, 'input[type="password"]'),
        (By.CSS_SELECTOR, 'input[name="password"]'),
        (By.ID, 'password'),
    ], timeout=10)

    email_el.clear(); email_el.send_keys(email)
    pw_el.clear(); pw_el.send_keys(password)

    try:
        submit = _first_present(driver, [
            (By.CSS_SELECTOR, 'button[type="submit"]'),
            (By.XPATH, "//button[contains(translate(., 'LOGIN', 'login'),'login') or contains(translate(., 'SIGN IN','sign in'),'sign in')]"),
            (By.CSS_SELECTOR, 'input[type="submit"]'),
        ], timeout=5)
        submit.click()
    except Exception:
        pw_el.submit()

    try:
        WebDriverWait(driver, wait).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Log out') or contains(., 'Logout')]")),
                EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Account') or contains(., 'My Account')]")),
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '$')]"))
            )
        )
        return True
    except TimeoutException:
        return False

def build_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,960")
    
    # Try different Chrome binary locations for Replit environment
    chrome_paths = [
        "/usr/bin/chromium-browser",
        "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            opts.binary_location = path
            break
    
    # Try different chromedriver paths
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
    
    if not chromedriver_path:
        raise RuntimeError("ChromeDriver not found")
    
    svc = Service(chromedriver_path)
    return webdriver.Chrome(service=svc, options=opts)

def scrape_product_enhanced(driver, item_number, logged_in=False):
    """Enhanced product scraping with better selectors"""
    print(f"Scraping item: {item_number}")
    
    try:
        url = f"https://www.pacificgiftware.com/product/{item_number}"
        driver.get(url)
        time.sleep(4)  # Wait for JavaScript to load
        
        result = {
            'Item Number': item_number,
            'Product Name': 'Not found',
            'Unit Price': 'Login required' if not logged_in else 'Not found',
            'Case Quantity': 'Not found',
            'Status': 'Processing'
        }
        
        # Get page source for analysis
        page_source = driver.page_source
        
        # Extract product name from page title or meta tags first
        title = driver.title
        if title and title != "Loading..." and "pacific" in title.lower():
            # Clean up title
            clean_title = title.replace(" | Pacific Trading", "").strip()
            if clean_title and len(clean_title) > 3:
                result['Product Name'] = clean_title
                result['Status'] = 'Found'
        
        # Try to find product name in page content
        name_xpath_selectors = [
            "//h1",
            "//h2",
            "//*[@class='product-title']",
            "//*[@class='product-name']",
            "//title",
            "//*[contains(@class, 'title')]"
        ]
        
        for xpath in name_xpath_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 5 and text != "Loading...":
                        result['Product Name'] = text
                        result['Status'] = 'Found'
                        break
                if result['Product Name'] != 'Not found':
                    break
            except:
                continue
        
        # Extract case quantity using multiple methods
        import re
        
        # Method 1: Search in page source
        case_patterns = [
            r'case\s*pack[:\s]*(\d+)',
            r'case\s*quantity[:\s]*(\d+)', 
            r'case[:\s]*(\d+)',
            r'pack[:\s]*(\d+)',
            r'qty[:\s]*(\d+)'
        ]
        
        for pattern in case_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                result['Case Quantity'] = matches[0]
                break
        
        # Method 2: Look for specific elements
        case_selectors = [
            "//*[contains(text(), 'CASE PACK')]",
            "//*[contains(text(), 'Case Pack')]", 
            "//*[contains(text(), 'case pack')]",
            "//*[contains(text(), 'Pack:')]",
            "//*[contains(text(), 'Quantity:')]"
        ]
        
        for selector in case_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        result['Case Quantity'] = numbers[0]
                        break
                if result['Case Quantity'] != 'Not found':
                    break
            except:
                continue
        
        # Try to get price (improved selectors for logged-in users)
        if logged_in:
            price_selectors = [
                # Material-UI specific selectors (from testing)
                "//h5[contains(@class, 'MuiTypography-h5') and contains(text(), '$')]",
                "//*[contains(@class, 'MuiTypography-h5') and contains(text(), '$')]",
                # Generic price selectors
                "//*[contains(@class, 'price')]",
                "//*[contains(@class, 'money')]", 
                "//*[contains(@class, 'current-price')]",
                "//*[contains(@class, 'product-price')]",
                "//span[contains(text(), '$')]",
                "//div[contains(text(), '$')]",
                "//*[@data-testid='price']",
                # Broad Material-UI typography containing $
                "//*[contains(@class, 'MuiTypography-root') and contains(text(), '$')]"
            ]
            
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip()
                        if '$' in text and len(text) < 30 and len(text) > 2:
                            # Filter out navigation prices or other non-product prices
                            if not any(word in text.lower() for word in ['cart', 'total', 'shipping', 'tax', 'free']):
                                result['Unit Price'] = text
                                break
                    if result['Unit Price'] != 'Not found':
                        break
                except:
                    continue
        
        print(f"  Name: {result['Product Name']}")
        print(f"  Price: {result['Unit Price']}")
        print(f"  Case: {result['Case Quantity']}")
        
        return result
        
    except Exception as e:
        print(f"  Error: {e}")
        return {
            'Item Number': item_number,
            'Product Name': f'Error: {str(e)}',
            'Unit Price': 'Error',
            'Case Quantity': 'Error',
            'Status': 'Error'
        }

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python final_scraper.py input.csv output.csv")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("Final Pacific Giftware Scraper")
    print("=" * 40)
    
    # Read items
    items = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0].strip():
                items.append(row[0].strip())
    
    print(f"Processing {len(items)} items")
    
    driver = build_driver()
    
    # Attempt login before scraping
    login_success = False
    try:
        login_success = login(driver)
        if login_success:
            print("✓ Login successful - prices will be available")
        else:
            print("⚠ Login failed - prices will show 'Login required'")
    except Exception as e:
        print(f"⚠ Login error: {e} - prices will show 'Login required'")
    
    try:
        results = []
        for i, item in enumerate(items, 1):
            print(f"\nItem {i}/{len(items)}: {item}")
            result = scrape_product_enhanced(driver, item, login_success)
            results.append(result)
        
        # Save results
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        
        print(f"\n✓ Final results saved to: {output_file}")
        
        # Summary
        found = len([r for r in results if r['Status'] == 'Found'])
        case_found = len([r for r in results if r['Case Quantity'] != 'Not found'])
        
        print(f"\nSummary:")
        print(f"Products found: {found}/{len(results)}")
        print(f"Case quantities found: {case_found}/{len(results)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()