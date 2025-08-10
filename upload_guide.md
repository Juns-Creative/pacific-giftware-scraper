# How to Upload Your Item Files

## Quick Steps:

1. **Prepare your file** - Create a CSV or Excel file with your item numbers
2. **Upload to Replit** - Drag and drop your file into the `scripts/pacificgiftware/` folder
3. **Run the scraper** - Use the web scraper tool to process your items

## File Format:

Your CSV file should look like this:
```
Item Number
10009
10010
10011
12345
67890
```

Or for Excel files, just put item numbers in the first column.

## Using the Web Scraper Tool:

Run: `python main.py --run web_scraper_tool.py`

The tool will:
- Help you set up credentials
- List your uploaded files
- Run the scraper automatically
- Show you the results

## Files You Can Upload:

- **CSV files** (.csv) - Simple comma-separated values
- **Excel files** (.xlsx, .xls) - Microsoft Excel format

Just drag and drop them into the `scripts/pacificgiftware/` folder in the file explorer!