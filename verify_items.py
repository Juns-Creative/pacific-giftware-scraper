#!/usr/bin/env python3
"""
Verify item access and test different formats
"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_item_formats(item_numbers):
    """Test different formats for item numbers"""
    
    base_urls = [
        "https://www.pacificgiftware.com/item/{}",
        "https://www.pacificgiftware.com/product/{}",
        "https://www.pacificgiftware.com/items/{}",
    ]
    
    prefixes = ["", "Y", "#"]
    
    print("🔍 Testing item number formats...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        for item in item_numbers:
            print(f"\n📦 Testing item: {item}")
            
            for prefix in prefixes:
                for base_url in base_urls:
                    test_item = f"{prefix}{item}"
                    url = base_url.format(test_item)
                    
                    try:
                        driver.get(url)
                        time.sleep(2)
                        
                        title = driver.title
                        current_url = driver.current_url
                        
                        if "not found" not in title.lower() and "error" not in title.lower():
                            print(f"  ✓ FOUND: {url}")
                            print(f"    Title: {title}")
                            
                            # Try to get some basic info
                            try:
                                h1 = driver.find_element("tag name", "h1")
                                print(f"    Product: {h1.text}")
                            except:
                                pass
                            
                            return url, test_item  # Return first working format
                        else:
                            print(f"  ❌ Not found: {url} (Title: {title})")
                            
                    except Exception as e:
                        print(f"  ❌ Error accessing {url}: {str(e)}")
        
        print("\n❌ No working formats found for these items")
        return None, None
        
    finally:
        driver.quit()

def test_known_working_items():
    """Test with previously working items"""
    print("🧪 Testing known working items...")
    
    known_items = ["12238", "11358", "Y7282"]
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        for item in known_items:
            clean_item = item.replace('Y', '')
            url = f"https://www.pacificgiftware.com/item/{clean_item}"
            
            print(f"\n📦 Testing known item: {item} -> {url}")
            
            driver.get(url)
            time.sleep(2)
            
            title = driver.title
            print(f"  Title: {title}")
            
            if "not found" not in title.lower():
                print(f"  ✓ Still accessible")
                try:
                    h1 = driver.find_element("tag name", "h1")
                    print(f"  Product: {h1.text}")
                except:
                    print("  ⚠️  No H1 found")
            else:
                print(f"  ❌ No longer accessible")
    
    finally:
        driver.quit()

def main():
    print("🔍 Pacific Giftware Item Verification")
    print("=" * 50)
    
    # Test known working items first
    test_known_working_items()
    
    # Test new items with different formats
    new_items = ['8990', '8773', '13841']
    working_url, working_format = test_item_formats(new_items)
    
    if working_url:
        print(f"\n✅ Found working format: {working_format}")
        print(f"✅ Working URL pattern: {working_url}")
    else:
        print("\n❌ These items may not exist in Pacific Giftware database")
        print("   Possible reasons:")
        print("   - Items don't exist")
        print("   - Items are discontinued") 
        print("   - Items require special authentication")
        print("   - Items are in a different product category")

if __name__ == "__main__":
    main()