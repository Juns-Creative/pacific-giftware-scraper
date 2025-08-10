#!/usr/bin/env python3
"""
Create downloadable files for the new test items
"""

import pandas as pd

def create_new_test_files():
    """Create Excel and CSV files for new test results"""
    
    # Read the test results
    df = pd.read_csv('scripts/pacificgiftware/test_with_y_results.csv')
    
    print("New Test Items Results")
    print("=" * 30)
    print(f"Items processed: {len(df)}")
    print(f"Successful: {len(df[df['Status'] == 'Found'])}")
    print()
    
    # Display results
    for index, row in df.iterrows():
        print(f"{row['Item Number']}: {row['Product Name']}")
        print(f"  Price: {row['Unit Price']}")
        print(f"  Case: {row['Case Quantity']}")
        print()
    
    # Create Excel file
    excel_file = 'New_Test_Items_Results.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='New Test Items', index=False)
        
        # Auto-adjust column widths
        workbook = writer.book
        worksheet = writer.sheets['New Test Items']
        
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
    
    # Create CSV file
    csv_file = 'New_Test_Items_Results.csv'
    df.to_csv(csv_file, index=False)
    
    print(f"✓ Excel file: {excel_file}")
    print(f"✓ CSV file: {csv_file}")
    
    return df

if __name__ == "__main__":
    create_new_test_files()