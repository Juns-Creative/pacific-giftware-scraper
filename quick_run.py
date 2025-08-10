#!/usr/bin/env python3
"""
Quick Run Script for Pacific Giftware Scraper
Easy-to-use interface for running the scraper with different item sets
"""

import os
import sys
import pandas as pd
from datetime import datetime

def create_sample_csv():
    """Create a sample CSV file with example items"""
    sample_items = ['Y7282', 'Y7750', '8791', '12238', '11358', '11982']
    
    with open('sample_items.csv', 'w') as f:
        f.write('Item Number\n')
        for item in sample_items:
            f.write(f'{item}\n')
    
    print("✓ Created sample_items.csv with example items")
    return 'sample_items.csv'

def check_credentials():
    """Check if login credentials are set"""
    email = os.environ.get('PACIFIC_EMAIL')
    password = os.environ.get('PACIFIC_PASSWORD')
    
    if not email or not password:
        print("⚠ Login credentials not set!")
        print("Please set your credentials:")
        print("export PACIFIC_EMAIL='your_email@domain.com'")
        print("export PACIFIC_PASSWORD='your_password'")
        return False
    
    print(f"✓ Login email set: {email}")
    return True

def run_scraper(input_file, output_file):
    """Run the Pacific Giftware scraper"""
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    if not check_credentials():
        return False
    
    # Run the scraper
    cmd = f"python scripts/final_scraper.py {input_file} {output_file}"
    print(f"Running: {cmd}")
    
    result = os.system(cmd)
    
    if result == 0:
        print(f"✓ Scraping completed successfully")
        print(f"✓ Results saved to: {output_file}")
        return True
    else:
        print("⚠ Scraping failed")
        return False

def create_excel_from_csv(csv_file):
    """Convert CSV results to Excel format"""
    if not os.path.exists(csv_file):
        print(f"CSV file '{csv_file}' not found")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        excel_file = csv_file.replace('.csv', '.xlsx')
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pacific Giftware Results', index=False)
            
            # Auto-adjust column widths
            workbook = writer.book
            worksheet = writer.sheets['Pacific Giftware Results']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Excel file created: {excel_file}")
        return excel_file
    
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return None

def show_results(csv_file):
    """Display scraping results summary"""
    if not os.path.exists(csv_file):
        return
    
    try:
        df = pd.read_csv(csv_file)
        
        print("\n" + "="*50)
        print("SCRAPING RESULTS SUMMARY")
        print("="*50)
        
        total_items = len(df)
        successful = len(df[df['Status'] == 'Found'])
        
        print(f"Total items processed: {total_items}")
        print(f"Successfully found: {successful}")
        print(f"Success rate: {successful/total_items*100:.1f}%")
        print()
        
        print("Detailed Results:")
        print("-" * 30)
        for index, row in df.iterrows():
            status_icon = "✓" if row['Status'] == 'Found' else "✗"
            print(f"{status_icon} {row['Item Number']}: {row['Product Name']}")
            if row['Status'] == 'Found':
                print(f"   Price: {row['Unit Price']} | Case: {row['Case Quantity']}")
            print()
        
    except Exception as e:
        print(f"Error reading results: {e}")

def main():
    """Main function with user interface"""
    
    print("Pacific Giftware Scraper - Quick Run")
    print("="*40)
    
    if len(sys.argv) < 2:
        print("Usage options:")
        print("1. python quick_run.py sample              # Run with sample items")
        print("2. python quick_run.py your_items.csv      # Run with your CSV file")
        print("3. python quick_run.py setup               # Create sample CSV file")
        print()
        print("Your CSV file should have this format:")
        print("Item Number")
        print("Y7282")
        print("Y7750")
        print("8791")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        create_sample_csv()
        print("\nNext steps:")
        print("1. Edit sample_items.csv with your item numbers")
        print("2. Set login credentials:")
        print("   export PACIFIC_EMAIL='your_email'")
        print("   export PACIFIC_PASSWORD='your_password'")
        print("3. Run: python quick_run.py sample_items.csv")
        return
    
    elif command == "sample":
        # Create and run sample
        input_file = create_sample_csv()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"sample_results_{timestamp}.csv"
    
    else:
        # Use provided CSV file
        input_file = command
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_results_{timestamp}.csv"
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Run the scraper
    success = run_scraper(input_file, output_file)
    
    if success:
        # Show results
        show_results(output_file)
        
        # Create Excel version
        excel_file = create_excel_from_csv(output_file)
        
        print("\n" + "="*50)
        print("FILES READY FOR DOWNLOAD:")
        print("="*50)
        print(f"📄 CSV: {output_file}")
        if excel_file:
            print(f"📊 Excel: {excel_file}")
        print()
        print("✓ Scraping job completed successfully!")

if __name__ == "__main__":
    main()