#!/usr/bin/env python3
"""
Create properly formatted output matching user's original Excel structure
"""

import pandas as pd

def create_formatted_output():
    # Read the comprehensive results
    results_df = pd.read_csv('Comprehensive_Results_20250809_070450/filled_data_20250809_070450.csv')
    
    # Create output matching user's exact column structure
    formatted_df = pd.DataFrame({
        'Item ': results_df['Item Number'],
        'Case Qty': results_df['Case Qty'], 
        'Unit price': results_df['Unit Price'],
        'URL': results_df['URL']
    })
    
    # Clean up the case quantity (remove text, keep numbers only)
    formatted_df['Case Qty'] = formatted_df['Case Qty'].apply(
        lambda x: int(x) if str(x).isdigit() else x
    )
    
    print("✓ Formatted data created:")
    print(formatted_df)
    
    # Save in multiple formats
    formatted_df.to_csv('Your_Filled_Data.csv', index=False)
    formatted_df.to_excel('Your_Filled_Data.xlsx', index=False) 
    
    print("\n📁 Files created:")
    print("   Your_Filled_Data.csv")
    print("   Your_Filled_Data.xlsx")
    
    return formatted_df

if __name__ == "__main__":
    create_formatted_output()