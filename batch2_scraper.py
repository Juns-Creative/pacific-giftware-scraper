#!/usr/bin/env python3
"""
Simple scraper for Batch 2 items: 8990, 8773, 13841
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
    """Set up Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_pacific_giftware(driver):
    """Login with working credentials"""
    try:
        print("🔐 Logging into Pacific Giftware...")
        driver.get("https://www.pacificgiftware.com/login")
        
        # Wait and find email field
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "mui-2"))
        )
        email_field.clear()
        email_field.send_keys("junscre@outlook.com")
        
        # Find password field
        password_field = driver.find_element(By.ID, "mui-3")
        password_field.clear()
        password_field.send_keys("pacific123")
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for login completion
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print("✓ Successfully logged in")
            return True
        else:
            print("❌ Login may have failed - still on login page")
            return False
            
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False

def scrape_item_data(driver, item_number):
    """Scrape data for a single item"""
    try:
        print(f"  🔍 Accessing item {item_number}...")
        
        # Navigate to item page
        url = f"https://www.pacificgiftware.com/item/{item_number}"
        driver.get(url)
        time.sleep(3)
        
        # Extract product data
        try:
            product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            try:
                product_name = driver.find_element(By.CSS_SELECTOR, "h1, .product-title, .item-name").text.strip()
            except:
                product_name = "Name not found"
        
        # Extract price with multiple selectors
        unit_price = "Price not found"
        price_selectors = [
            "span.price",
            ".price-display", 
            "[data-testid='price']",
            ".product-price",
            ".wholesale-price",
            "span:contains('$')"
        ]
        
        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                if price_element and '$' in price_element.text:
                    unit_price = price_element.text.strip()
                    break
            except:
                continue
        
        # Extract case quantity
        case_quantity = "Case info not found"
        try:
            # Look for C/number pattern
            page_text = driver.page_source
            import re
            case_match = re.search(r'C/(\d+)', page_text)
            if case_match:
                case_quantity = case_match.group(1)
        except:
            pass
        
        result = {
            'Item Number': item_number,
            'Product Name': product_name,
            'Unit Price': unit_price,
            'Case Quantity': case_quantity,
            'Status': 'Found'
        }
        
        print(f"  ✓ {product_name} - {unit_price} (Case: {case_quantity})")
        return result
        
    except Exception as e:
        print(f"  ❌ Error scraping {item_number}: {str(e)}")
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Unit Price': 'Error', 
            'Case Quantity': 'Error',
            'Status': f'Error: {str(e)}'
        }

def main():
    """Main scraping function for batch 2 items"""
    items = ['8990', '8773', '13841']
    
    print("🚀 Pacific Giftware Scraper - Batch 2")
    print(f"Items to scrape: {items}")
    print("=" * 50)
    
    # Create results folder
    folder_name = "Batch2_Results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✓ Created folder: {folder_name}")
    
    driver = setup_chrome_driver()
    
    try:
        # Login
        if not login_to_pacific_giftware(driver):
            print("❌ Cannot proceed without login")
            return
        
        # Scrape all items
        results = []
        for i, item_number in enumerate(items, 1):
            print(f"\n📦 Processing item {i}/{len(items)}: {item_number}")
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
        print(f"📊 Results saved:")
        print(f"   📄 {csv_file}")
        print(f"   📊 {excel_file}")
        
        # Display results
        print("\n📋 Results Summary:")
        print(df.to_string(index=False))
        
        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()