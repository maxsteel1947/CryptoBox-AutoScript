from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re   
import os

# Set the debugging address to connect to an existing Chrome tab (replace with the correct address)
debugging_address = 'localhost:9222'

# Create ChromeOptions and specify the debugging address
chrome_options = webdriver.ChromeOptions()
chrome_options.debugger_address = debugging_address

# Create a WebDriver instance using ChromeOptions
chrome_driver = webdriver.Chrome(options=chrome_options)

# Navigate to the specific page you want to interact with
url = 'https://www.binance.com/en/my/wallet/account/payment/cryptobox'  # Replace with your URL
chrome_driver.get(url)

# Load the Excel sheet created by tg.py
tg_excel_filename = 'Your directory/extracted_data.xlsx'

# Read the Excel file created by tg.py
df = pd.read_excel(tg_excel_filename)

# Extract box codes from the Excel file and filter only alphanumeric codes with 8 characters
box_codes = df['Extracted Data'].tolist()
alphanumeric_codes = [code for code in box_codes if re.match(r'^[A-Za-z0-9]{8}$', code)]

# Set the path for the claimed boxes file
claimed_boxes_file = 'Yourdirectory/claimed_boxes.txt'

# Load the list of claimed boxes from "claimed_boxes.txt" if the file exists
claimed_boxes = set()
if os.path.exists(claimed_boxes_file):
    with open(claimed_boxes_file, 'r') as file:
        claimed_boxes = set(file.read().splitlines())

# Define the list of blocked codes
blocklist = [
    "Disculpa", "kTFlgDEA", "escribir", "telegram", "activity", "Lembarek", "adivinas", "Festival",
    "RLUJVFKH", "vacation", "Telegram", "MIQYNEGS", "pedirles", "BVBLEDGJ", "26692826", "CURRENCY",
    "8zEkSxXk", "comentar", "9XvDmZLK", "JPHPYVLH", "everyone", "INDUSTRY", "telegram", "ADOPTION",
    "question", "boxtiger", "Scammers", "51768000", "kZ4v7GZA", "l8mmvhjy", "1tvc8qc5", "kZ4v7GZA",
    "NDNIINXT", "EDXRRYKQ", "F1BULIAM", "RHUEQRFJ", "I9WY0KCL", "ADXJY02T","Xsloaner", "EQJIDWAN",
    "horrible","hcNasqmr","ACCIDENT","M8vAsj3j",'Channels', 'settings','contacts','security','SCAMMERS',
    'Scammers','everyone','prometan','CEYIMLMF','jMAbnNO4','kZ4v7GZA','traducir'
]
def contains_only_letters(s):
    return bool(re.match(r'^[A-Za-z]+$', s))

def contains_only_numbers(s):
    return bool(re.match(r'^[0-9]+$', s))

def filter_and_block_message(message):
    if not contains_only_letters(message) and not contains_only_numbers(message):
        print(f"Blocked message: {message}")
        return True
    else:
        return False

# Function to validate and process alphanumeric 8-character codes
def process_code(code):
    if len(code) == 8 and code.isalnum():
        # Interact with the page as needed
        input_field = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter box code"]'))
        )
        input_field.clear()  # Clear any existing text
        input_field.send_keys(code)

        claim_button = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[text()="Claim Now"]'))
        )
        
        # Attempt to click the "Claim Now" button, ignoring any element intercepting clicks
        try:
            claim_button.click()
        except:
            pass

        claimed_boxes.add(code)
        with open(claimed_boxes_file, 'a') as file:
            file.write(code + '\n')

    else:
        print(f"Invalid code for box: {code}")

try:
    for box_code in alphanumeric_codes:
        # Check if the box code is in the blocklist
        if box_code in blocklist:
            print(f"Blocked code: {box_code}")
            continue  # Skip this box code

        # Check if the box code has been claimed
        if box_code in claimed_boxes:
            print(f"Box already claimed: {box_code}")
            continue  # Skip this box code

        # Process the valid alphanumeric 8-character code
        cleaned_code = re.sub(r'[^A-Za-z0-9]', '', box_code)  # Filter out non-alphanumeric characters

        # Interact with the page as needed
        input_field = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter box code"]'))
        )
        input_field.clear()  # Clear any existing text
        input_field.send_keys(cleaned_code)

        claim_button = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[text()="Claim Now"]'))
        )

        # Attempt to click the "Claim Now" button, ignoring any element intercepting clicks
        try:
            claim_button.click()
        except:
            pass

        claimed_boxes.add(cleaned_code)
        with open(claimed_boxes_file, 'a') as file:
            file.write(cleaned_code + '\n')

        # Check if an error message for an invalid code is present
        error_message = None
        try:
            error_message = WebDriverWait(chrome_driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//div[text()="Invalid code, please double check the code and try again."]'))
            )
        except Exception as e:
            pass

        # Check if the "Open" button with text "Open" is present
        open_button = None
        try:
            open_button = WebDriverWait(chrome_driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1jwn9gn div.css-6xx5k5')) ##find this by inspecting element open button
            )
        except Exception as e:
            pass

        # Check if the "Crypto Box Details" text is present
        crypto_details = None
        try:
            crypto_details = WebDriverWait(chrome_driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Crypto Box Details")]'))
            )

        except Exception as e:
            pass

        if open_button:
            # Click the "Open" button on the popup
            open_button.click()
            time.sleep(2)  # Wait for 2 seconds (adjust as needed)

        # Refresh the page for the next box code
        if error_message:
            print(f"Invalid code for box: {box_code}")
            chrome_driver.refresh()
            time.sleep(2)  # Add a 2-second delay after refreshing the page

        elif crypto_details:
            # Use JavaScript to forcefully reload the page
            chrome_driver.execute_script("location.reload()")
            time.sleep(2)  # Add a 2-second delay after refreshing the page
        else:
            chrome_driver.refresh()
            time.sleep(2)  # Add a 2-second delay after refreshing the page

except Exception as e:
    print(f"An error occurred: {str(e)}")

# Quit the Chrome WebDriver to release resources
chrome_driver.refresh()
