#!/usr/bin/env python3
"""
Working scraper for Batch 2 items using correct URL structure
"""

import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import re

def setup_chrome_driver():
    """Set up Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_item_data(driver, item_number):
    """Scrape data for a single item using correct URL structure"""
    try:
        print(f"  🔍 Processing item {item_number}...")
        
        # Use the working URL pattern: /product/ instead of /item/
        url = f"https://www.pacificgiftware.com/product/{item_number}"
        driver.get(url)
        time.sleep(3)
        
        # Check page title
        page_title = driver.title
        print(f"    Page: {page_title}")
        
        if "not found" in page_title.lower():
            return {
                'Item Number': item_number,
                'Product Name': 'Item not found',
                'Unit Price': 'N/A',
                'Case Quantity': 'N/A',
                'Status': 'Not Found'
            }
        
        # Extract product name from title (it's already in the title)
        product_name = page_title.split(' | ')[0].strip() if ' | ' in page_title else page_title
        
        # Also try to get from H1
        try:
            h1_element = driver.find_element(By.TAG_NAME, "h1")
            if h1_element and h1_element.text.strip():
                product_name = h1_element.text.strip()
        except:
            pass
        
        # Extract price information from page source
        unit_price = "Price not available"
        try:
            page_source = driver.page_source
            
            # Look for price patterns in page source
            price_patterns = [
                r'\$(\d+\.\d{2})',
                r'Price[:\s]*\$(\d+\.\d{2})',
                r'Cost[:\s]*\$(\d+\.\d{2})',
                r'Wholesale[:\s]*\$(\d+\.\d{2})'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    unit_price = f"${matches[0]}"
                    break
        except:
            pass
        
        # Extract case quantity from product name or page
        case_quantity = "Case info not available"
        try:
            # Look for C/number pattern in product name first
            case_match = re.search(r'C/(\d+)', product_name)
            if case_match:
                case_quantity = case_match.group(1)
            else:
                # Look in page source
                page_source = driver.page_source
                case_patterns = [
                    r'C/(\d+)',
                    r'Case of (\d+)',
                    r'Pack of (\d+)',
                    r'(\d+) per case'
                ]
                
                for pattern in case_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        case_quantity = matches[0]
                        break
        except:
            pass
        
        result = {
            'Item Number': item_number,
            'Product Name': product_name,
            'Unit Price': unit_price,
            'Case Quantity': case_quantity,
            'Status': 'Found'
        }
        
        print(f"  ✓ {product_name}")
        print(f"    Price: {unit_price} | Case: {case_quantity}")
        
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
    """Main scraping function for batch 2 items"""
    items = ['8990', '8773', '13841']
    
    print("🚀 Pacific Giftware Scraper - Batch 2 (Fixed URL Structure)")
    print(f"Items to process: {', '.join(items)}")
    print("=" * 60)
    
    # Create results folder
    folder_name = "Batch2_Results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✓ Created folder: {folder_name}")
    else:
        print(f"✓ Using existing folder: {folder_name}")
    
    driver = setup_chrome_driver()
    
    try:
        # Scrape all items (no login required for basic product info)
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
        
        # Display results table
        print(f"\n📋 Results Summary:")
        print(df.to_string(index=False, max_colwidth=40))
        
        # Count successful items
        found_items = len(df[df['Status'] == 'Found'])
        print(f"\n✅ Successfully processed: {found_items}/{len(items)} items")
        
        return results
        
    finally:
        driver.quit()
        print("\n🔒 Browser session closed")

if __name__ == "__main__":
    main()