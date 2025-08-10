#!/usr/bin/env python3
"""
Quick Run Script with Custom Folder Support
Usage: python quick_folder_run.py <items_file> <output_folder>
"""

import sys
import os
from organized_scraper import scrape_with_custom_folder

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_folder_run.py <items_file> [output_folder]")
        print("\nExamples:")
        print("  python quick_folder_run.py my_items.csv")
        print("  python quick_folder_run.py my_items.xlsx january_results")
        print("  python quick_folder_run.py items.csv client_abc_orders")
        return
    
    items_file = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(items_file):
        print(f"❌ File not found: {items_file}")
        return
    
    print(f"🚀 Pacific Giftware Scraper")
    print(f"📂 Input file: {items_file}")
    print(f"📁 Output folder: {output_folder or 'auto-generated'}")
    print("=" * 50)
    
    try:
        result = scrape_with_custom_folder(
            input_file=items_file,
            output_folder=output_folder
        )
        
        if result:
            results, folder_path = result
            print(f"\n✅ Success! Results saved to: {folder_path}")
        else:
            print("❌ Scraping failed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()