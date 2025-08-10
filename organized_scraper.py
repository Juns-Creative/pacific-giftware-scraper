#!/usr/bin/env python3
"""
Pacific Giftware Scraper with Custom Output Folders
Saves results to user-specified folders for better organization
"""

import os
import sys
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def create_output_folder(folder_name=None):
    """Create output folder if it doesn't exist"""
    if folder_name is None:
        # Use timestamp if no folder name provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"results_{timestamp}"
    
    # Ensure folder name is safe for filesystem
    safe_folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    if not os.path.exists(safe_folder_name):
        os.makedirs(safe_folder_name)
        print(f"✓ Created folder: {safe_folder_name}")
    else:
        print(f"✓ Using existing folder: {safe_folder_name}")
    
    return safe_folder_name

def setup_chrome_driver():
    """Set up Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_pacific_giftware(driver):
    """Login to Pacific Giftware with authentication"""
    try:
        print("🔐 Logging into Pacific Giftware...")
        driver.get("https://www.pacificgiftware.com/login")
        
        # Wait and find email field (Material-UI selector)
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mui-2"))
        )
        email_field.send_keys("junscre@outlook.com")
        
        # Find password field (Material-UI selector)
        password_field = driver.find_element(By.ID, "mui-3")
        password_field.send_keys("pacific123")
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(3)
        print("✓ Successfully logged in")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False

def scrape_item_data(driver, item_number):
    """Scrape data for a single item"""
    try:
        # Clean item number (remove any prefixes)
        clean_item = item_number.strip().replace('Y', '').replace('#', '')
        
        # Navigate to item page
        url = f"https://www.pacificgiftware.com/item/{clean_item}"
        driver.get(url)
        time.sleep(2)
        
        # Extract product data
        try:
            product_name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            product_name = "Name not found"
        
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, "span.price, .price-display, [data-testid='price']")
            unit_price = price_element.text
        except:
            unit_price = "Price not found"
        
        try:
            case_element = driver.find_element(By.XPATH, "//span[contains(text(), 'C/')]")
            case_quantity = case_element.text.split('C/')[1].split()[0]
        except:
            case_quantity = "Case info not found"
        
        return {
            'Item Number': item_number,
            'Product Name': product_name,
            'Unit Price': unit_price,
            'Case Quantity': case_quantity,
            'Status': 'Found'
        }
        
    except Exception as e:
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Unit Price': 'Error',
            'Case Quantity': 'Error',
            'Status': f'Error: {str(e)}'
        }

def save_results(results, output_folder, base_filename="pacific_giftware_results"):
    """Save results to CSV and Excel in specified folder"""
    df = pd.DataFrame(results)
    
    # Create filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_folder, f"{base_filename}_{timestamp}.csv")
    excel_file = os.path.join(output_folder, f"{base_filename}_{timestamp}.xlsx")
    
    # Save CSV
    df.to_csv(csv_file, index=False)
    print(f"✓ CSV saved: {csv_file}")
    
    # Save Excel
    df.to_excel(excel_file, index=False)
    print(f"✓ Excel saved: {excel_file}")
    
    return csv_file, excel_file

def scrape_with_custom_folder(input_file=None, output_folder=None, item_numbers=None):
    """Main scraping function with custom folder support"""
    
    # Create output folder
    if output_folder is None:
        output_folder = input("Enter folder name for results (or press Enter for auto-generated): ").strip()
    
    folder_path = create_output_folder(output_folder)
    
    # Get item numbers
    if item_numbers is None:
        if input_file and os.path.exists(input_file):
            # Read from file
            if input_file.endswith('.xlsx'):
                df = pd.read_excel(input_file)
            else:
                df = pd.read_csv(input_file)
            
            # Try different column names for item numbers
            item_col = None
            for col in ['Item Number', 'Item', 'Item#', 'SKU', 'Product Code']:
                if col in df.columns:
                    item_col = col
                    break
            
            if item_col:
                item_numbers = df[item_col].astype(str).tolist()
            else:
                print("❌ Could not find item number column in file")
                return
        else:
            # Manual input
            print("Enter item numbers (one per line, press Enter twice to finish):")
            item_numbers = []
            while True:
                item = input("Item: ").strip()
                if not item:
                    break
                item_numbers.append(item)
    
    if not item_numbers:
        print("❌ No item numbers provided")
        return
    
    print(f"🚀 Starting scrape for {len(item_numbers)} items...")
    print(f"📁 Results will be saved to: {folder_path}")
    
    # Set up browser and login
    driver = setup_chrome_driver()
    
    try:
        if not login_to_pacific_giftware(driver):
            print("❌ Cannot proceed without login")
            return
        
        # Scrape all items
        results = []
        for i, item_number in enumerate(item_numbers, 1):
            print(f"🔍 Scraping item {i}/{len(item_numbers)}: {item_number}")
            result = scrape_item_data(driver, item_number)
            results.append(result)
            
            # Show progress
            if result['Status'] == 'Found':
                print(f"  ✓ {result['Product Name']} - {result['Unit Price']}")
            else:
                print(f"  ❌ {result['Status']}")
        
        # Save results to custom folder
        csv_file, excel_file = save_results(results, folder_path)
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Results saved to folder: {folder_path}")
        print(f"📄 Files created:")
        print(f"   - {os.path.basename(csv_file)}")
        print(f"   - {os.path.basename(excel_file)}")
        
        return results, folder_path
        
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line usage
        input_file = sys.argv[1]
        output_folder = sys.argv[2] if len(sys.argv) > 2 else None
        scrape_with_custom_folder(input_file=input_file, output_folder=output_folder)
    else:
        # Interactive usage
        print("Pacific Giftware Scraper with Custom Folders")
        print("=" * 50)
        
        choice = input("1. Use CSV/Excel file\n2. Enter items manually\nChoice (1 or 2): ").strip()
        
        if choice == "1":
            input_file = input("Enter CSV/Excel filename: ").strip()
            output_folder = input("Enter folder name for results (optional): ").strip() or None
            scrape_with_custom_folder(input_file=input_file, output_folder=output_folder)
        elif choice == "2":
            output_folder = input("Enter folder name for results (optional): ").strip() or None
            scrape_with_custom_folder(output_folder=output_folder)
        else:
            print("Invalid choice")