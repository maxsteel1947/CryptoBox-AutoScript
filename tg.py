from telethon import TelegramClient, events
import re
import os
import pandas as pd
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)

# Replace with your actual API credentials and phone number - Get this from telegram
api_id = 'Your API ID'
api_hash = 'Your API Hash'
phone_number = '+Your phone number'

# Specify the chat or channel you want to monitor (by username or chat ID)
chat_username = 'Telegram Group you want to monitor'

# Create a TelegramClient instance
client = TelegramClient('my_telegram_app', api_id, api_hash)

# Define the regex pattern to match 8-character alphanumeric codes
pattern = r'\b[A-Za-z0-9]{8}\b'

# Define the path and filename for the Excel file
excel_filename = 'extracted_data.xlsx'


# Create an empty DataFrame or load the existing one if the file exists
if os.path.exists(excel_filename):
    df = pd.read_excel(excel_filename)
else:
    df = pd.DataFrame(columns=['Extracted Data'])
    

# Create an empty list to store extracted codes
extracted_codes = []

# Function to save data to an Excel file
def save_to_excel(data):
    unique_codes = list(set(data))
    new_df = pd.DataFrame(unique_codes, columns=['Extracted Data'])
    df_concat = pd.concat([df, new_df], ignore_index=True)  # Concatenate new data with existing data
    df_concat.to_excel(excel_filename, index=False)

# Define your event handler for incoming messages
@client.on(events.NewMessage(chats=chat_username))
async def handle_new_message(event):
    message_text = event.message.text  # Define message_text here
        
    # Use regex to find 8-character alphanumeric codes
    codes = re.findall(pattern, message_text)
    if codes:
        # Filter out non-alphanumeric characters from the extracted codes
        valid_codes = [re.sub(r'[^A-Za-z0-9]', '', code) for code in codes]
        valid_codes = list(filter(lambda x: len(x) == 8, valid_codes))  # Filter for 8-character codes

        if valid_codes:
            extracted_codes.extend(valid_codes)
            # Add the double-filtered codes to the Excel file only
            save_to_excel(extracted_codes)

        # Print a message to confirm that a message was received
        print("Message received:", message_text)

# Start the TelegramClient with your bot token
with client:
    print("Program is running...")
    client.run_until_disconnected()
