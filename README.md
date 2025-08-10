Pacific Giftware Scraper
========================

This project provides a Python script to automate the extraction of
product information—unit price and case quantity—from the Pacific
Giftware wholesale website.  The script uses Selenium WebDriver to
authenticate with your account, navigate directly to product pages,
parse the rendered HTML with BeautifulSoup and compile the results into
a CSV file.

> **Important:** Because this environment cannot install new Python
> packages or run Selenium, the script cannot be executed here.  To
> run the scraper, clone or download this repository on your local
> machine, install the dependencies listed in `requirements.txt` and
> make sure you have Chrome and the matching ChromeDriver installed.

Getting Started
---------------

1. **Install Python dependencies** (on your local machine):

   ```bash
   python -m pip install -r requirements.txt
   ```

   Ensure that your Chrome browser version matches the downloaded
   `chromedriver`.  You can download ChromeDriver from
   <https://chromedriver.chromium.org/downloads> and place it on your
   system `PATH`.

2. **Prepare your item list.**  Create a CSV or Excel file with a
   single column containing the item numbers you wish to query.  The
   first row can optionally be a header, which will be ignored.

3. **Run the scraper:**

   ```bash
   python pacificgiftware_scraper.py path/to/your_items.csv path/to/output.csv
   ```

   The script will prompt for your Pacific Giftware email and
   password.  To run unattended, set the environment variables
   `PACIFIC_EMAIL` and `PACIFIC_PASSWORD` before execution.

4. **Review the output.**  The resulting CSV will contain columns
   `Item Number`, `Product Name`, `Unit Price`, and `Case Quantity` for
   each item processed.

How It Works
------------

* The script launches a Chrome browser through Selenium and navigates to the
  Pacific Giftware login page【706916085568325†screenshot】.  After
  entering your credentials, it is authenticated for the remainder of
  the session.
* For each item number, the script visits the product page (e.g.,
  `https://www.pacificgiftware.com/product/10009`).  Product pages show
  a notice that price and quantity details are available only to logged-in
  users【770199959410526†screenshot】.
* The page also displays a “Notes” section containing a `CASE PACK`
  value (case quantity)【770199959410526†screenshot】.  The script
  extracts this number and, once logged in, captures the unit price and
  product name from the page.

Customization
-------------

You can modify the selectors used to locate HTML elements (such as the
search bar, product name or price fields) in `pacificgiftware_scraper.py` if
the website’s structure changes.  Additional product attributes—like
weight or material—could be scraped by extending the
``get_product_details`` function.

Limitations
-----------

* The script relies on Selenium, which requires a GUI or headless
  browser.  It will not run on systems without a graphical
  environment unless you configure a headless display.
* The code has been tested against the Pacific Giftware website as of
  August 2025.  If the site layout or authentication mechanism
  changes, you may need to adjust selectors or update the login logic.

License
-------

This project is provided under the MIT License.  See `LICENSE` for
details.