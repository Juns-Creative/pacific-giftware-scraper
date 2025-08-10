#!/usr/bin/env python3
"""
Extract item numbers from the uploaded Excel file
"""

import pandas as pd
import os

def extract_items_from_excel():
    """Extract item numbers from the uploaded Excel file"""
    
    excel_file = "attached_assets/Item # (1)_1754718653622.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return
    
    try:
        # Try reading the Excel file
        print(f"Reading Excel file: {excel_file}")
        
        # Try different sheet approaches
        try:
            df = pd.read_excel(excel_file)
            print("✓ Successfully read Excel file")
        except Exception as e:
            print(f"Error reading Excel: {e}")
            # Try reading specific sheet
            try:
                df = pd.read_excel(excel_file, sheet_name=0)
                print("✓ Successfully read first sheet")
            except Exception as e2:
                print(f"Error reading first sheet: {e2}")
                return
        
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        # Display the data
        print("Data preview:")
        print(df.head(10))
        print()
        
        # Try to identify item number column
        item_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['item', 'product', 'number', 'code', 'id']):
                item_columns.append(col)
        
        print(f"Potential item columns: {item_columns}")
        
        # Extract item numbers
        items = []
        if item_columns:
            # Use the first item column found
            item_col = item_columns[0]
            print(f"Using column: {item_col}")
            
            for value in df[item_col].dropna():
                # Clean and extract numeric part
                item_str = str(value).strip()
                if item_str and item_str != 'nan':
                    # Try to extract numbers
                    import re
                    numbers = re.findall(r'\d+', item_str)
                    if numbers:
                        items.append(numbers[0])
                    else:
                        items.append(item_str)
        else:
            # Try first column
            print("No specific item column found, using first column")
            first_col = df.columns[0]
            for value in df[first_col].dropna():
                item_str = str(value).strip()
                if item_str and item_str != 'nan':
                    import re
                    numbers = re.findall(r'\d+', item_str)
                    if numbers:
                        items.append(numbers[0])
                    else:
                        items.append(item_str)
        
        # Remove duplicates and clean
        items = list(set([item for item in items if item and len(str(item)) > 0]))
        
        print(f"Extracted {len(items)} unique items: {items}")
        
        # Create CSV file for testing
        if items:
            test_csv = "scripts/pacificgiftware/test_items.csv"
            with open(test_csv, 'w') as f:
                f.write("Item Number\n")
                for item in items:
                    f.write(f"{item}\n")
            
            print(f"✓ Created test file: {test_csv}")
            print(f"Ready to test with: {', '.join(items)}")
            return items
        else:
            print("⚠ No items found in the file")
            return []
            
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return []

if __name__ == "__main__":
    extract_items_from_excel()