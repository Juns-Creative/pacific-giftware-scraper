#!/usr/bin/env python3
"""
Simple Product Information Scraper
==================================

This script provides a basic HTTP-based scraper for Pacific Giftware as a fallback
when Selenium is not available. Note: This may have limitations compared to the 
full Selenium-based scraper since the website uses JavaScript.
"""

import os
import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict

def read_items_from_csv(csv_file: str) -> List[str]:
    """Read item numbers from CSV file."""
    items = []
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if present
            for row in reader:
                if row and row[0].strip():
                    items.append(row[0].strip())
        return items
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def scrape_product_basic(item_number: str) -> Dict[str, str]:
    """
    Basic HTTP scraper for Pacific Giftware product pages.
    Note: Limited functionality since the site uses JavaScript for pricing.
    """
    url = f"https://www.pacificgiftware.com/product/{item_number}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract basic product information
        product_name = "Not found"
        unit_price = "Login required"
        case_quantity = "Not found"
        
        # Look for product title
        title_selectors = ['h1', '.product-title', '[data-testid="product-title"]', '.pdp-product-name']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                product_name = element.get_text(strip=True)
                break
        
        # Look for case pack information in various places
        case_selectors = [
            '.case-pack', '.case-quantity', '[data-testid="case-pack"]',
            'span:contains("CASE PACK")', 'div:contains("CASE PACK")',
            'span:contains("case pack")', 'div:contains("case pack")'
        ]
        
        for selector in case_selectors:
            if ':contains(' in selector:
                # Handle text-based selectors
                continue
            element = soup.select_one(selector)
            if element:
                case_quantity = element.get_text(strip=True)
                break
        
        # Look for case pack in text content
        page_text = soup.get_text()
        import re
        case_match = re.search(r'CASE PACK[:\s]*(\d+)', page_text, re.IGNORECASE)
        if case_match:
            case_quantity = case_match.group(1)
        
        return {
            'Item Number': item_number,
            'Product Name': product_name,
            'Unit Price': unit_price,
            'Case Quantity': case_quantity,
            'Status': 'Scraped (Basic)' if product_name != "Not found" else 'Not Found'
        }
        
    except requests.RequestException as e:
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Unit Price': 'Error',
            'Case Quantity': 'Error',
            'Status': f'Network Error: {str(e)}'
        }
    except Exception as e:
        return {
            'Item Number': item_number,
            'Product Name': 'Error',
            'Unit Price': 'Error', 
            'Case Quantity': 'Error',
            'Status': f'Parse Error: {str(e)}'
        }

def process_items_simple(input_file: str, output_file: str):
    """Process items using basic HTTP scraping."""
    print("Simple Product Information Scraper")
    print("=" * 40)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Read items
    items = read_items_from_csv(input_file)
    if not items:
        print("No items found in input file.")
        return
    
    print(f"Found {len(items)} items to process:")
    for item in items:
        print(f"  - {item}")
    print()
    
    results = []
    
    for i, item in enumerate(items, 1):
        print(f"Processing item {i}/{len(items)}: {item}")
        result = scrape_product_basic(item)
        results.append(result)
        print(f"  Status: {result['Status']}")
        print(f"  Product: {result['Product Name']}")
        print()
    
    # Save results
    try:
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")
        print("\nSummary:")
        print(f"Total items processed: {len(results)}")
        print(f"Successful: {len([r for r in results if 'Error' not in r['Status']])}")
        print(f"Errors: {len([r for r in results if 'Error' in r['Status']])}")
        
        return output_file
        
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

def main():
    """Main function for simple scraper."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python simple_scraper.py input.csv output.csv")
        print("\nThis is a basic HTTP scraper that works without browser automation.")
        print("Note: Pricing information requires login, so this scraper can only")
        print("extract product names and case quantities that are visible to anonymous users.")
        print("\nFor full functionality including pricing, use the Selenium-based scraper locally.")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    process_items_simple(input_file, output_file)

if __name__ == "__main__":
    main()