#!/usr/bin/env python3
"""
Comprehensive Pacific Giftware Data Filler
Reads Excel/CSV with item numbers and fills in Case Qty, Unit Price, and URL
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
import re

def setup_chrome_driver():
    """Set up Chrome driver for scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_pacific_giftware(driver):
    """Attempt login for wholesale pricing access"""
    try:
        print("Attempting login for pricing access...")
        driver.get("https://www.pacificgiftware.com/login")
        time.sleep(3)
        
        # Try multiple login strategies
        login_strategies = [
            # Strategy 1: Material-UI selectors
            {
                'email_selector': (By.ID, "mui-2"),
                'password_selector': (By.ID, "mui-3"),
                'method': 'Material-UI'
            },
            # Strategy 2: Standard selectors
            {
                'email_selector': (By.CSS_SELECTOR, "input[type='email']"),
                'password_selector': (By.CSS_SELECTOR, "input[type='password']"),
                'method': 'Standard'
            }
        ]
        
        for strategy in login_strategies:
            try:
                print(f"Trying {strategy['method']} login method...")
                
                # Find email field
                email_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(strategy['email_selector'])
                )
                email_field.clear()
                email_field.send_keys("junscre@outlook.com")
                
                # Find password field
                password_field = driver.find_element(*strategy['password_selector'])
                password_field.clear()
                password_field.send_keys("pacific123")
                
                # Click login button
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'LOG IN')]")
                login_button.click()
                
                time.sleep(5)
                
                # Check if login successful
                if "login" not in driver.current_url.lower():
                    print(f"✓ Login successful using {strategy['method']} method")
                    return True
                    
            except Exception as e:
                print(f"Login attempt with {strategy['method']} failed: {str(e)}")
                continue
        
        print("⚠️  All login attempts failed - proceeding without authentication")
        return False
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def extract_comprehensive_data(driver, item_number, with_login=False):
    """Extract comprehensive data for an item"""
    try:
        # Clean item number
        clean_item = str(item_number).strip().replace('Y', '').replace('#', '')
        
        # Try both URL patterns
        urls_to_try = [
            f"https://www.pacificgiftware.com/product/{clean_item}",
            f"https://www.pacificgiftware.com/item/{clean_item}"
        ]
        
        working_url = None
        product_data = None
        
        for url in urls_to_try:
            try:
                print(f"    Trying: {url}")
                driver.get(url)
                time.sleep(2)
                
                page_title = driver.title
                
                if "not found" not in page_title.lower() and "error" not in page_title.lower():
                    working_url = url
                    print(f"    ✓ Found at: {url}")
                    break
                    
            except Exception as e:
                continue
        
        if not working_url:
            return {
                'Item Number': item_number,
                'Product Name': 'Item not found',
                'Case Qty': 'N/A',
                'Unit Price': 'N/A',
                'URL': 'Item not available',
                'Status': 'Not Found'
            }
        
        # Extract product name
        product_name = "Name not available"
        try:
            # Try page title first
            page_title = driver.title
            if ' | ' in page_title:
                product_name = page_title.split(' | ')[0].strip()
            
            # Try H1 element
            try:
                h1_element = driver.find_element(By.TAG_NAME, "h1")
                if h1_element.text.strip():
                    product_name = h1_element.text.strip()
            except:
                pass
                
        except Exception as e:
            pass
        
        # Extract case quantity
        case_quantity = "Not specified"
        try:
            # Look in product name first
            case_match = re.search(r'C/(\d+)', product_name)
            if case_match:
                case_quantity = case_match.group(1)
            else:
                # Search page source
                page_source = driver.page_source
                case_patterns = [
                    r'C/(\d+)',
                    r'Case of (\d+)',
                    r'Pack of (\d+)',
                    r'(\d+) per case',
                    r'Quantity[:\s]*(\d+)'
                ]
                
                for pattern in case_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        case_quantity = matches[0]
                        break
                        
        except Exception as e:
            pass
        
        # Extract unit price
        unit_price = "Login required for pricing"
        if with_login:
            try:
                # Look for price elements with multiple selectors
                price_selectors = [
                    "span.price",
                    ".price-display", 
                    "[data-testid='price']",
                    ".product-price",
                    ".wholesale-price",
                    ".price",
                    "span:contains('$')"
                ]
                
                for selector in price_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element and '$' in element.text:
                                unit_price = element.text.strip()
                                break
                        if unit_price != "Login required for pricing":
                            break
                    except:
                        continue
                
                # Also search page source for price patterns
                if unit_price == "Login required for pricing":
                    page_source = driver.page_source
                    price_patterns = [
                        r'\$(\d+\.\d{2})',
                        r'Price[:\s]*\$(\d+\.\d{2})',
                        r'Wholesale[:\s]*\$(\d+\.\d{2})'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, page_source)
                        if matches:
                            unit_price = f"${matches[0]}"
                            break
                            
            except Exception as e:
                pass
        
        result = {
            'Item Number': item_number,
            'Product Name': product_name,
            'Case Qty': case_quantity,
            'Unit Price': unit_price,
            'URL': working_url,
            'Status': 'Found'
        }
        
        print(f"    ✓ {product_name}")
        print(f"      Case: {case_quantity} | Price: {unit_price}")
        
        return result
        
    except Exception as e:
        print(f"    ❌ Error processing {item_number}: {str(e)}")
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Case Qty': 'Error',
            'Unit Price': 'Error',
            'URL': 'Error',
            'Status': f'Error: {str(e)}'
        }

def fill_comprehensive_data(input_file):
    """Main function to fill comprehensive data"""
    
    # Read input file
    try:
        if input_file.endswith('.xlsx'):
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file)
        
        print(f"Input file columns: {list(df.columns)}")
        print(f"Total items: {len(df)}")
        
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Find item number column
    item_column = None
    possible_columns = ['Item Number', 'Item', 'Item#', 'Item #', 'SKU', 'Product Code', 'Number']
    
    for col in df.columns:
        if any(possible_col.lower() in col.lower() for possible_col in possible_columns):
            item_column = col
            break
    
    if not item_column:
        print(f"Could not find item number column. Available columns: {list(df.columns)}")
        return
    
    print(f"Using column '{item_column}' for item numbers")
    
    # Get item numbers
    item_numbers = df[item_column].astype(str).tolist()
    print(f"Processing {len(item_numbers)} items...")
    
    # Setup browser
    driver = setup_chrome_driver()
    
    try:
        # Attempt login for pricing
        logged_in = login_to_pacific_giftware(driver)
        
        # Process all items
        results = []
        for i, item_number in enumerate(item_numbers, 1):
            print(f"\n📦 Processing item {i}/{len(item_numbers)}: {item_number}")
            result = extract_comprehensive_data(driver, item_number, with_login=logged_in)
            results.append(result)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output folder
        folder_name = f"Comprehensive_Results_{timestamp}"
        os.makedirs(folder_name, exist_ok=True)
        
        csv_file = os.path.join(folder_name, f"filled_data_{timestamp}.csv")
        excel_file = os.path.join(folder_name, f"filled_data_{timestamp}.xlsx")
        
        output_df.to_csv(csv_file, index=False)
        output_df.to_excel(excel_file, index=False)
        
        print(f"\n🎉 Processing completed!")
        print(f"📁 Results saved to: {folder_name}/")
        print(f"   📄 CSV: {os.path.basename(csv_file)}")
        print(f"   📊 Excel: {os.path.basename(excel_file)}")
        
        # Display summary
        print(f"\n📊 Summary:")
        found_items = len(output_df[output_df['Status'] == 'Found'])
        print(f"   ✅ Successfully processed: {found_items}/{len(item_numbers)} items")
        
        # Display sample results
        print(f"\n📋 Sample Results:")
        print(output_df[['Item Number', 'Product Name', 'Case Qty', 'Unit Price']].head().to_string(index=False))
        
        return output_df, folder_name
        
    finally:
        driver.quit()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter input file (CSV/Excel): ").strip()
    
    if os.path.exists(input_file):
        fill_comprehensive_data(input_file)
    else:
        print(f"File not found: {input_file}")