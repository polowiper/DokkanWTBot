import os
import time
import json
import requests
from datetime import datetime
from update_data import update_data
# Create the fetches folder if it doesn't exist
if not os.path.exists('fetches'):
    os.makedirs('fetches')

# Set the counter for the filename
filename_counter = 268

def save_json_to_file(data, filename):
    with open(f'fetches/{filename}', 'w') as f:
        json.dump(data, f, indent=4)

def fetch_data():
    response = requests.get('https://dokkan.wiki/api/budokai/53/players?with_ids=true&page=1&size=1000')
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    return data


# Fetch data every 15 minutes
while True:
    try:
        data = fetch_data()
        filename = f'fetch{filename_counter}.json'
        save_json_to_file(data, filename)
        filename_counter += 1
        print(f'Data fetched and saved to {os.path.join("fetches", filename)}')
        update_data(data, "data.json")
    except Exception as e:
        print(f'Error fetching data: {e}')

    # Wait for 15 minutes
    time.sleep(15 * 60)
