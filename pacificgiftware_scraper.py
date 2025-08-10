"""
pacificgiftware_scraper.py
---------------------------

This module automates the process of logging into the Pacific Giftware
website, visiting product pages for a list of item numbers, extracting
pricing and case quantity information, and writing the results to a CSV
file.  It is designed to be modular so that each step (logging in,
loading a product page, parsing product information, and writing
results) can be developed, tested, and maintained independently.

The website renders most of its content via client‑side JavaScript,
including the login flow and product details.  As a result, simple
HTTP requests using the ``requests`` library are not sufficient for
interacting with the site.  Instead, this script uses Selenium
WebDriver to control a real browser session.  Selenium allows us to
perform the same actions a human user would: navigate to the login
page, enter credentials, click the log in button, and wait for
elements to appear on the page.

To use this script you'll need:

* Google Chrome (or another browser) installed on your system.
* The matching ChromeDriver binary placed on your PATH.  See
  https://chromedriver.chromium.org/downloads for downloads and
  installation instructions.
* The ``selenium`` Python package installed.  It can be installed
  via pip::

    pip install selenium

Because this script deals with credentials, it never stores your
username or password in the source code.  Instead, it prompts the
user at runtime.  If you wish to automate this further (for example,
running the script unattended), you can set the ``PACIFIC_EMAIL`` and
``PACIFIC_PASSWORD`` environment variables before running the script.

The primary entry point is the :func:`process_items` function, which
reads a list of item numbers from an input CSV or Excel file,
iterates through them, and writes the results to an output CSV.
``process_items`` calls helper functions for each logical step in the
workflow: ``login``, ``get_product_details``, and ``write_results``.

Note
----
This script cannot be executed successfully in the current agent
environment because we do not have access to Pacific Giftware login
credentials or a GUI browser.  However, the functions are written
such that a user running this code locally can test each component.

"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import List, Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup

# Selenium imports.  These modules are optional until you call
# functions that require them; importing at the top makes IDEs aware
# of the dependency.
# NOTE: We intentionally avoid importing Selenium at module import time.
# Selenium is an optional dependency used only when actually scraping
# data.  Importing it at the top would cause the whole module to
# fail on systems where Selenium isn't installed.  Instead, the
# necessary classes are imported within the functions that require
# them.  This allows auxiliary functions like ``read_item_numbers``
# and ``write_results`` to be tested even without Selenium.


@dataclass
class ProductInfo:
    """Container for product information extracted from the website."""

    item_number: str
    product_name: str
    unit_price: Optional[str]
    case_quantity: Optional[str]

    def to_dict(self) -> Dict[str, str]:
        """Return a dictionary representation suitable for CSV output."""
        return {
            "Item Number": self.item_number,
            "Product Name": self.product_name,
            "Unit Price": self.unit_price or "",
            "Case Quantity": self.case_quantity or "",
        }


from typing import Any

def start_driver(headless: bool = False) -> Any:
    """
    Start a Selenium WebDriver session.

    Parameters
    ----------
    headless : bool, optional
        If ``True``, the browser will run without a GUI.  Running in
        headless mode can be useful for automated scripts that don't
        require visual feedback.  If you're developing or debugging
        this script, set ``headless=False`` to see the browser window.

    Returns
    -------
    webdriver.Chrome
        An instance of the Chrome WebDriver.

    Raises
    ------
    FileNotFoundError
        If ChromeDriver is not found on the system PATH.
    RuntimeError
        If the driver cannot be started for any other reason.
    """
    # Lazy import of Selenium.  This raises ImportError only if the user
    # actually calls ``start_driver`` without Selenium installed.
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService

    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless=new")  # Use the new headless mode for Chrome ≥ 109
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")

    # Many corporate environments block connections to websites that
    # aren't pre‑approved.  We disable the Chrome "enable automation"
    # banner to reduce noise during manual testing.
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Specify the Chrome binary path for this environment
    chrome_options.binary_location = "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium-browser"

    # Initialise the ChromeDriver service.  If the chromedriver binary
    # isn't found on your PATH, this will raise a FileNotFoundError.
    try:
        # Specify the chromedriver path explicitly
        chromedriver_path = "/nix/store/8zj50jw4w0hby47167kqqsaqw4mm5bkd-chromedriver-unwrapped-138.0.7204.100/bin/chromedriver"
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as exc:
        raise RuntimeError("Failed to start ChromeDriver. Ensure that Chrome and the matching "
                           "ChromeDriver executable are installed and on your PATH.") from exc
    return driver


def login(driver: Any, email: str, password: str, timeout: int = 30) -> None:
    """
    Log into the Pacific Giftware website.

    Navigates to the login page, enters the provided credentials, and
    waits until the login is complete.  After this function returns,
    the driver session should be authenticated for the remainder of
    the script.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium WebDriver instance controlling the browser.
    email : str
        The user's email address used for logging in.
    password : str
        The user's password.
    timeout : int, optional
        Maximum number of seconds to wait for the login process to
        complete.

    Raises
    ------
    TimeoutError
        If the login process takes longer than ``timeout`` seconds.
    Exception
        If input elements cannot be found or the login button is not clickable.
    """
    # Navigate to the login page.
    driver.get("https://www.pacificgiftware.com/pages/login")

    # Lazy import of Selenium modules used for waiting and element location.
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, timeout)

    # Locate the email and password fields.  These elements are
    # identified using their labels in the DOM.  If the website's
    # structure changes, these locators may need to be updated.
    email_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    password_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )

    # Clear any pre‑filled text and enter the credentials.
    email_input.clear()
    email_input.send_keys(email)
    password_input.clear()
    password_input.send_keys(password)

    # Find and click the login button.
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button, input[type='submit']"))
    )
    login_button.click()

    # Wait for a page element that only appears once logged in.  On
    # Pacific Giftware, product pages display a price field once
    # authenticated.  Here we wait for the home page search bar to be
    # clickable as a simple proxy for a successful login.  Adjust the
    # selector if the site layout changes.
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Search']"))
    )


def extract_case_quantity_from_notes(notes_text: str) -> Optional[str]:
    """
    Extract the case quantity from a notes string.

    On each product page, there is a notes section with free text
    containing lines such as ``CASE PACK: 1`` or ``CASE PACK: 12``.
    This function searches the notes for a line beginning with
    ``CASE PACK`` (case insensitive) and returns the numeric value if
    found.

    Parameters
    ----------
    notes_text : str
        The contents of the notes field, including newline characters.

    Returns
    -------
    Optional[str]
        The case quantity (number as a string) if found, otherwise
        ``None``.
    """
    if not notes_text:
        return None
    for line in notes_text.splitlines():
        if "case pack" in line.lower():
            # Split on colon and strip whitespace.  Some notes may be
            # formatted as "CASE PACK: 1" while others use hyphens or
            # different punctuation.  We normalise by splitting on
            # non‑digit characters and extracting the first group of
            # digits.
            parts = line.split(":")
            if len(parts) >= 2:
                candidate = parts[1].strip()
                # Extract digits from the candidate.
                digits = "".join(ch for ch in candidate if ch.isdigit())
                if digits:
                    return digits
            # Fallback: search for digits in the entire line.
            digits = "".join(ch for ch in line if ch.isdigit())
            if digits:
                return digits
    return None


def get_product_details(driver: Any, item_number: str, timeout: int = 30) -> ProductInfo:
    """
    Load a product page and extract details.

    Given an item number, this function navigates directly to
    ``https://www.pacificgiftware.com/product/{item_number}``, waits for
    the page to load, and then parses the page source with
    BeautifulSoup to extract the product name, unit price, and case
    quantity.  If certain information is not available (for example,
    price before logging in), the corresponding field will be set to
    ``None``.

    Parameters
    ----------
    driver : webdriver.Chrome
        An authenticated Selenium WebDriver session.
    item_number : str
        The product's SKU or item number as listed on Pacific Giftware.
    timeout : int, optional
        How long to wait for the product page to load before giving up.

    Returns
    -------
    ProductInfo
        An object containing the extracted details.

    Raises
    ------
    TimeoutError
        If the product page does not load within the specified timeout.
    """
    url = f"https://www.pacificgiftware.com/product/{item_number}"
    driver.get(url)
    # Lazy import of Selenium classes used for waiting and selecting elements.
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, timeout)

    # Wait for the product title to be present on the page.  The title
    # appears inside an <h1> tag according to the current site layout.
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    # Grab the page source once all dynamic content has been rendered.
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Extract the product name.  We look for the first <h1> tag.
    name_tag = soup.find("h1")
    product_name = name_tag.get_text(strip=True) if name_tag else ""

    # Extract unit price.  Logged‑in users should see a price element on
    # the page.  In Pacific Giftware's markup, prices are displayed
    # inside elements with class names containing 'price'.  We'll look
    # for any span or div that contains a dollar sign.  If nothing is
    # found, the unit price will remain None.
    unit_price: Optional[str] = None
    price_candidates = soup.find_all(string=lambda s: s and "$" in s)
    # Filter out irrelevant matches such as meta tags or script text.
    for cand in price_candidates:
        # Skip script/style tags
        if cand.parent.name in {"script", "style"}:
            continue
        text = cand.strip()
        # Basic sanity check: valid price strings should start with '$'
        # and contain digits.
        if text.startswith("$") and any(ch.isdigit() for ch in text):
            unit_price = text
            break

    # Extract case quantity from the notes section.  The notes are
    # typically found in a <div> with a label 'Notes:'.  We'll search
    # for a sibling element containing the word 'CASE PACK'.
    case_quantity: Optional[str] = None
    # Find any element containing 'Notes:' and look at its following
    # siblings for the text.
    notes_label = soup.find(string=lambda s: isinstance(s, str) and s.strip().lower() == "notes:")
    if notes_label:
        parent = notes_label.parent
        # The next sibling often contains the actual notes text.
        notes_container = parent.find_next_sibling()
        notes_text = notes_container.get_text(separator="\n", strip=True) if notes_container else ""
        case_quantity = extract_case_quantity_from_notes(notes_text)

    return ProductInfo(
        item_number=item_number,
        product_name=product_name,
        unit_price=unit_price,
        case_quantity=case_quantity,
    )


def read_item_numbers(input_path: str) -> List[str]:
    """
    Read item numbers from a CSV or Excel file.

    The input file should contain a single column with item numbers.  Any
    blank lines or additional columns are ignored.  This function uses
    ``pandas`` to handle both CSV and Excel formats automatically.

    Parameters
    ----------
    input_path : str
        Path to the CSV or Excel file containing item numbers.

    Returns
    -------
    List[str]
        A list of item numbers as strings.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If the file format is unsupported or the file is empty.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")

    # Determine file extension and use pandas accordingly.
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    if ext in {".csv", ".txt"}:
        df = pd.read_csv(input_path, dtype=str)
    elif ext in {".xls", ".xlsx"}:
        df = pd.read_excel(input_path, dtype=str)
    else:
        raise ValueError(f"Unsupported file extension '{ext}'. Please provide a CSV or Excel file.")

    # Drop completely empty rows and columns.
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    if df.empty:
        raise ValueError("Input file is empty or contains no item numbers.")

    # Assume the first column contains the item numbers.
    first_col = df.columns[0]
    items = df[first_col].astype(str).str.strip().tolist()

    # Filter out any blank strings.
    items = [item for item in items if item]
    return items


def write_results(output_path: str, products: List[ProductInfo]) -> None:
    """
    Write product information to a CSV file.

    Parameters
    ----------
    output_path : str
        Path to the output CSV file.  If the file already exists, it
        will be overwritten.
    products : List[ProductInfo]
        A list of ProductInfo objects containing the scraped data.
    """
    fieldnames = ["Item Number", "Product Name", "Unit Price", "Case Quantity"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            writer.writerow(product.to_dict())


def process_items(input_path: str, output_path: str, headless: bool = False) -> None:
    """
    Main workflow to process multiple items and save their details.

    This function orchestrates the overall scraping process.  It prompts
    the user for login credentials (unless environment variables are
    provided), logs into the site, iterates over each item number from
    the input file, scrapes the product details, and writes the
    results to a CSV file.

    Parameters
    ----------
    input_path : str
        Path to the input CSV or Excel file containing item numbers.
    output_path : str
        Path where the output CSV file will be written.
    headless : bool, optional
        If True, run the browser in headless mode.

    Raises
    ------
    Exception
        If any part of the login or scraping process fails.  Errors
        are propagated so that they can be handled by the caller.
    """
    # Read list of item numbers.
    item_numbers = read_item_numbers(input_path)
    if not item_numbers:
        print("No item numbers found in the input file.")
        return

    # Obtain credentials from environment variables or prompt the user.
    email = os.environ.get("PACIFIC_EMAIL")
    password = os.environ.get("PACIFIC_PASSWORD")
    if not email:
        email = input("Enter your Pacific Giftware email: ").strip()
    if not password:
        # Use getpass to hide password input if available.
        try:
            import getpass
            password = getpass.getpass("Enter your Pacific Giftware password: ")
        except Exception:
            password = input("Enter your Pacific Giftware password: ").strip()

    # Start the browser.
    driver = start_driver(headless=headless)
    try:
        # Log in.  If login fails, an exception will be raised.
        login(driver, email=email, password=password)

        # Iterate through items and collect product info.
        products: List[ProductInfo] = []
        for item in item_numbers:
            print(f"Processing item {item}...")
            try:
                info = get_product_details(driver, item)
                products.append(info)
            except Exception as exc:
                print(f"Failed to process item {item}: {exc}")
                products.append(
                    ProductInfo(
                        item_number=item,
                        product_name="",
                        unit_price=None,
                        case_quantity=None,
                    )
                )

        # Write out the results.
        write_results(output_path, products)
        print(f"Done. Wrote {len(products)} records to {output_path}.")
    finally:
        # Always quit the browser to free resources.
        driver.quit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape product details from Pacific Giftware")
    parser.add_argument("input", help="Path to the input CSV or Excel file with item numbers")
    parser.add_argument("output", help="Path to the output CSV file")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    args = parser.parse_args()

    process_items(args.input, args.output, headless=args.headless)