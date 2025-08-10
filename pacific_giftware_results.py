#!/usr/bin/env python3
"""
Create downloadable Excel file from Pacific Giftware scraping results
"""

import pandas as pd
import os

def create_excel_file():
    """Create Excel file from CSV results"""
    
    # Read the complete results
    csv_file = 'scripts/pacificgiftware/complete_results.csv'
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        return
    
    # Read CSV data
    df = pd.read_csv(csv_file)
    
    print("Pacific Giftware Scraping Results")
    print("=" * 40)
    print(f"Total items processed: {len(df)}")
    print(f"Successful extractions: {len(df[df['Status'] == 'Found'])}")
    print()
    
    # Display the data
    print("Results:")
    for index, row in df.iterrows():
        print(f"{row['Item Number']}: {row['Product Name']}")
        print(f"  Price: {row['Unit Price']}")
        print(f"  Case Qty: {row['Case Quantity']}")
        print()
    
    # Create Excel file
    excel_file = 'Pacific_Giftware_Results.xlsx'
    
    # Create Excel with formatting
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Product Data', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Product Data']
        
        # Auto-adjust column widths
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
    
    # Also copy CSV to root for easy download
    csv_download = 'Pacific_Giftware_Results.csv'
    df.to_csv(csv_download, index=False)
    print(f"✓ CSV file created: {csv_download}")
    
    return excel_file, csv_download

if __name__ == "__main__":
    create_excel_file()