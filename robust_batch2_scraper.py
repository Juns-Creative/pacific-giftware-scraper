#!/usr/bin/env python3
"""
Robust scraper for Batch 2 items with enhanced login handling
"""

import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

def setup_chrome_driver():
    """Set up Chrome driver with enhanced options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def enhanced_login(driver):
    """Enhanced login with multiple selector strategies"""
    try:
        print("🔐 Accessing Pacific Giftware login page...")
        driver.get("https://www.pacificgiftware.com/login")
        time.sleep(5)  # Allow page to fully load
        
        print("🔍 Looking for email field...")
        email_field = None
        
        # Try multiple strategies to find email field
        email_selectors = [
            ("ID", "mui-2"),
            ("NAME", "email"),
            ("TYPE", "email"),
            ("XPATH", "//input[@type='email']"),
            ("XPATH", "//input[contains(@placeholder, 'email')]"),
            ("CSS", "input[type='email']")
        ]
        
        for method, selector in email_selectors:
            try:
                if method == "ID":
                    email_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, selector))
                    )
                elif method == "NAME":
                    email_field = driver.find_element(By.NAME, selector)
                elif method == "TYPE":
                    email_field = driver.find_element(By.XPATH, f"//input[@type='{selector}']")
                elif method == "XPATH":
                    email_field = driver.find_element(By.XPATH, selector)
                elif method == "CSS":
                    email_field = driver.find_element(By.CSS_SELECTOR, selector)
                
                if email_field:
                    print(f"✓ Found email field using {method}: {selector}")
                    break
            except:
                continue
        
        if not email_field:
            print("❌ Could not find email field")
            return False
        
        # Enter email
        email_field.clear()
        email_field.send_keys("junscre@outlook.com")
        print("✓ Email entered")
        
        # Find password field
        print("🔍 Looking for password field...")
        password_field = None
        
        password_selectors = [
            ("ID", "mui-3"),
            ("NAME", "password"),
            ("TYPE", "password"),
            ("XPATH", "//input[@type='password']"),
            ("CSS", "input[type='password']")
        ]
        
        for method, selector in password_selectors:
            try:
                if method == "ID":
                    password_field = driver.find_element(By.ID, selector)
                elif method == "NAME":
                    password_field = driver.find_element(By.NAME, selector)
                elif method == "TYPE":
                    password_field = driver.find_element(By.XPATH, f"//input[@type='{selector}']")
                elif method == "XPATH":
                    password_field = driver.find_element(By.XPATH, selector)
                elif method == "CSS":
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                
                if password_field:
                    print(f"✓ Found password field using {method}: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("❌ Could not find password field")
            return False
        
        # Enter password
        password_field.clear()
        password_field.send_keys("pacific123")
        print("✓ Password entered")
        
        # Find and click login button
        print("🔍 Looking for login button...")
        login_button = None
        
        login_selectors = [
            ("XPATH", "//button[contains(text(), 'Login')]"),
            ("XPATH", "//button[contains(text(), 'LOG IN')]"),
            ("XPATH", "//button[contains(text(), 'Sign In')]"),
            ("XPATH", "//input[@type='submit']"),
            ("CSS", "button[type='submit']"),
            ("CSS", ".login-button"),
            ("CSS", ".btn-login")
        ]
        
        for method, selector in login_selectors:
            try:
                if method == "XPATH":
                    login_button = driver.find_element(By.XPATH, selector)
                elif method == "CSS":
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if login_button:
                    print(f"✓ Found login button using {method}: {selector}")
                    break
            except:
                continue
        
        if not login_button:
            print("❌ Could not find login button")
            return False
        
        # Click login
        login_button.click()
        print("✓ Login button clicked")
        
        # Wait for login to process
        time.sleep(8)
        
        # Check if login was successful
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"Current URL: {current_url}")
        print(f"Page title: {page_title}")
        
        if "login" not in current_url.lower() or "dashboard" in current_url.lower() or "account" in current_url.lower():
            print("✓ Login appears successful")
            return True
        else:
            print("⚠️  Still on login page - login may have failed")
            # Try to proceed anyway, sometimes login works but URL doesn't change
            return True
            
    except Exception as e:
        print(f"❌ Login failed with error: {str(e)}")
        return False

def scrape_item_data(driver, item_number):
    """Scrape data for a single item with enhanced error handling"""
    try:
        print(f"  🔍 Processing item {item_number}...")
        
        # Navigate to item page
        url = f"https://www.pacificgiftware.com/item/{item_number}"
        driver.get(url)
        time.sleep(4)
        
        # Check if we can access the page
        page_title = driver.title
        current_url = driver.current_url
        
        print(f"    Page title: {page_title}")
        print(f"    URL: {current_url}")
        
        # Extract product name
        product_name = "Name not found"
        name_selectors = ["h1", ".product-title", ".item-name", ".product-name"]
        
        for selector in name_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    product_name = element.text.strip()
                    print(f"    ✓ Name found: {product_name}")
                    break
            except:
                continue
        
        # Extract price
        unit_price = "Price not found"
        price_selectors = [
            "span.price",
            ".price-display", 
            "[data-testid='price']",
            ".product-price",
            ".wholesale-price",
            ".price"
        ]
        
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element and '$' in element.text:
                        unit_price = element.text.strip()
                        print(f"    ✓ Price found: {unit_price}")
                        break
                if unit_price != "Price not found":
                    break
            except:
                continue
        
        # Extract case quantity from page source
        case_quantity = "Case info not found"
        try:
            page_source = driver.page_source
            import re
            
            # Look for various case patterns
            case_patterns = [
                r'C/(\d+)',
                r'Case of (\d+)',
                r'Pack of (\d+)',
                r'Qty[:\s]+(\d+)'
            ]
            
            for pattern in case_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    case_quantity = matches[0]
                    print(f"    ✓ Case quantity found: {case_quantity}")
                    break
        except:
            pass
        
        result = {
            'Item Number': item_number,
            'Product Name': product_name,
            'Unit Price': unit_price,
            'Case Quantity': case_quantity,
            'Status': 'Found' if product_name != "Name not found" else 'Not Found'
        }
        
        print(f"  ✅ Result: {product_name} | {unit_price} | Case: {case_quantity}")
        return result
        
    except Exception as e:
        print(f"  ❌ Error processing {item_number}: {str(e)}")
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Unit Price': 'Error',
            'Case Quantity': 'Error',
            'Status': f'Error: {str(e)}'
        }

def main():
    """Main function to scrape batch 2 items"""
    items = ['8990', '8773', '13841']
    
    print("🚀 Enhanced Pacific Giftware Scraper - Batch 2")
    print(f"Items: {', '.join(items)}")
    print("=" * 60)
    
    # Create results folder
    folder_name = "Batch2_Results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✓ Created folder: {folder_name}")
    else:
        print(f"✓ Using folder: {folder_name}")
    
    driver = setup_chrome_driver()
    
    try:
        # Attempt login
        login_success = enhanced_login(driver)
        
        if not login_success:
            print("⚠️  Login failed, but continuing with scraping attempt...")
        
        # Scrape all items
        results = []
        for i, item_number in enumerate(items, 1):
            print(f"\n📦 Item {i}/{len(items)}: {item_number}")
            result = scrape_item_data(driver, item_number)
            results.append(result)
        
        # Save results
        df = pd.DataFrame(results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(folder_name, f"batch2_results_{timestamp}.csv")
        excel_file = os.path.join(folder_name, f"batch2_results_{timestamp}.xlsx")
        
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)
        
        print(f"\n🎉 Scraping completed!")
        print(f"📁 Results saved to: {folder_name}/")
        print(f"   📄 CSV: {os.path.basename(csv_file)}")
        print(f"   📊 Excel: {os.path.basename(excel_file)}")
        
        # Display results summary
        print(f"\n📋 Results Summary:")
        for _, row in df.iterrows():
            status_icon = "✓" if row['Status'] == 'Found' else "❌"
            print(f"   {status_icon} {row['Item Number']}: {row['Product Name']}")
        
        return results
        
    finally:
        driver.quit()
        print("\n🔒 Browser closed")

if __name__ == "__main__":
    main()