#!/usr/bin/env python3
"""
Quick Scrape - Simple wrapper for web scraping
This makes it easy to run the web scraper tool without navigating menus.
"""

import os
import sys
from pathlib import Path

def main():
    """Quick access to web scraping functionality."""
    print("Quick Scrape Tool")
    print("================")
    print("This tool helps you scrape Pacific Giftware product information quickly.")
    print()
    
    # Check for uploaded files
    scraper_dir = Path("scripts/pacificgiftware")
    csv_files = list(scraper_dir.glob("*.csv"))
    excel_files = list(scraper_dir.glob("*.xlsx")) + list(scraper_dir.glob("*.xls"))
    
    # Filter out the sample file and script files
    input_files = []
    for f in csv_files + excel_files:
        if f.name not in ["sample_items.csv", "pacificgiftware_scraper.py"]:
            input_files.append(f)
    
    if not input_files:
        print("📁 No input files found yet.")
        print()
        print("To get started:")
        print("1. Upload your CSV or Excel file with item numbers to: scripts/pacificgiftware/")
        print("2. Run this script again")
        print()
        print("Or use the full web scraper tool: python main.py --run web_scraper_tool.py")
        return
    
    print(f"📄 Found {len(input_files)} input file(s):")
    for f in input_files:
        print(f"   - {f.name}")
    print()
    
    # Check credentials
    email = os.environ.get('PACIFIC_EMAIL')
    password = os.environ.get('PACIFIC_PASSWORD')
    
    if not (email and password):
        print("⚠️  Credentials not set!")
        print("Set your Pacific Giftware credentials:")
        print("   export PACIFIC_EMAIL='your_email@domain.com'")
        print("   export PACIFIC_PASSWORD='your_password'")
        print()
    else:
        print(f"✅ Credentials set for: {email}")
        print()
    
    print("Ready to scrape! Run the full tool for interactive options:")
    print("   python main.py --run web_scraper_tool.py")
    print()
    print("Or run the scraper directly:")
    print(f"   cd scripts/pacificgiftware")
    print(f"   python pacificgiftware_scraper.py your_file.csv output.csv --headless")

if __name__ == "__main__":
    main()