#!/usr/bin/env python3
"""
Wrapper script to run the Pacific Giftware scraper.
This allows you to run the scraper through the main Python environment interface.
"""

import os
import sys
import subprocess

def main():
    """Run the Pacific Giftware scraper."""
    print("Pacific Giftware Scraper Wrapper")
    print("=" * 40)
    
    scraper_dir = os.path.join(os.path.dirname(__file__), "pacificgiftware")
    scraper_path = os.path.join(scraper_dir, "pacificgiftware_scraper.py")
    
    if not os.path.exists(scraper_path):
        print(f"Error: Scraper not found at {scraper_path}")
        return 1
    
    print("Usage instructions:")
    print("1. Create a CSV file with your item numbers (one per line)")
    print("2. Set environment variables: PACIFIC_EMAIL and PACIFIC_PASSWORD")
    print("3. Run with: python main.py --run run_pacificgiftware.py")
    print("")
    print("Example command when running directly:")
    print(f"cd {scraper_dir}")
    print("python pacificgiftware_scraper.py input.csv output.csv")
    print("")
    
    # Change to scraper directory and show help
    os.chdir(scraper_dir)
    
    print("Scraper help:")
    print("-" * 20)
    subprocess.run([sys.executable, "pacificgiftware_scraper.py", "--help"])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())