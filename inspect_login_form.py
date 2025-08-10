#!/usr/bin/env python3
"""
Inspect the actual login form HTML structure
"""

import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def build_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,960")
    
    chrome_paths = [
        "/usr/bin/chromium-browser",
        "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            opts.binary_location = path
            break
    
    chromedriver_paths = [
        shutil.which("chromedriver"),
        "/usr/bin/chromedriver",
        "/nix/store/8zj50jw4w0hby47167kqqsaqw4mm5bkd-chromedriver-unwrapped-138.0.7204.100/bin/chromedriver"
    ]
    
    chromedriver_path = None
    for path in chromedriver_paths:
        if path and os.path.exists(path):
            chromedriver_path = path
            break
    
    svc = Service(chromedriver_path)
    return webdriver.Chrome(service=svc, options=opts)

def inspect_login_form():
    driver = build_driver()
    
    try:
        url = "https://www.pacificgiftware.com/pages/login"
        print(f"Inspecting login form at: {url}")
        
        driver.get(url)
        time.sleep(5)  # Wait for page to fully load
        
        print(f"Page title: {driver.title}")
        
        # Get all input elements
        print("\n=== All Input Elements ===")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type") or "text"
                input_name = input_elem.get_attribute("name") or "no-name"
                input_id = input_elem.get_attribute("id") or "no-id"
                input_class = input_elem.get_attribute("class") or "no-class"
                input_placeholder = input_elem.get_attribute("placeholder") or "no-placeholder"
                
                print(f"Input {i+1}:")
                print(f"  Type: {input_type}")
                print(f"  Name: {input_name}")
                print(f"  ID: {input_id}")
                print(f"  Class: {input_class}")
                print(f"  Placeholder: {input_placeholder}")
                print()
            except Exception as e:
                print(f"Error reading input {i+1}: {e}")
        
        # Get all form elements
        print("\n=== All Form Elements ===")
        forms = driver.find_elements(By.TAG_NAME, "form")
        for i, form in enumerate(forms):
            try:
                form_action = form.get_attribute("action") or "no-action"
                form_method = form.get_attribute("method") or "no-method"
                form_class = form.get_attribute("class") or "no-class"
                
                print(f"Form {i+1}:")
                print(f"  Action: {form_action}")
                print(f"  Method: {form_method}")
                print(f"  Class: {form_class}")
                print()
            except Exception as e:
                print(f"Error reading form {i+1}: {e}")
        
        # Get all button elements
        print("\n=== All Button Elements ===")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            try:
                button_type = button.get_attribute("type") or "no-type"
                button_text = button.text or "no-text"
                button_class = button.get_attribute("class") or "no-class"
                
                print(f"Button {i+1}:")
                print(f"  Type: {button_type}")
                print(f"  Text: {button_text}")
                print(f"  Class: {button_class}")
                print()
            except Exception as e:
                print(f"Error reading button {i+1}: {e}")
        
        # Search for specific patterns in page source
        print("\n=== Page Source Analysis ===")
        page_source = driver.page_source
        
        # Look for email-related patterns
        import re
        email_patterns = [
            r'input[^>]*email[^>]*>',
            r'input[^>]*type="email"[^>]*>',
            r'input[^>]*name="[^"]*email[^"]*"[^>]*>',
            r'input[^>]*placeholder="[^"]*email[^"]*"[^>]*>'
        ]
        
        print("Email field patterns found:")
        for pattern in email_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"Pattern '{pattern}': {len(matches)} matches")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"  {match}")
        
        # Look for text-type inputs that might be email fields
        text_inputs = re.findall(r'<input[^>]*type=["\']?text["\']?[^>]*>', page_source, re.IGNORECASE)
        print(f"\nFound {len(text_inputs)} text input fields:")
        for i, text_input in enumerate(text_inputs[:5]):  # Show first 5
            print(f"  {i+1}: {text_input}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_login_form()