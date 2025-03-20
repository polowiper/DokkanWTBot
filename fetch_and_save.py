import os
import time
import json
import requests
from datetime import datetime, timedelta
from update_db import update_data
from config import USER_AGENT, API_TOKEN, WT_EDITION
import sys
def save_json_to_file(data, filename):
    with open(f'fetches/{filename}', 'w') as f:
        json.dump(data, f, indent=4)


def latest_fetch():
    output_dir = "fetches"
    i = 0
    while True:
        filename = f"fetch{i}.json"
        file_path = os.path.join(output_dir, filename)
        if not os.path.exists(file_path):
           break
        i += 1
    return f"{output_dir}/fetch{i-1}.json" if os.path.exists(os.path.join(output_dir, f"fetch{i-1}.json")) else None


def fetch_data(size: int=1000):
    headers = {
        'x-apitoken': API_TOKEN,
        'User-Agent': USER_AGENT
    }
    response = requests.get(f'https://dokkan.wiki/api/budokai/{WT_EDITION}/players/live?size={size}', headers=headers)
    #response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    return data


def dynamic_print(last_fetch, updated_time, next_api_call):
    sys.stdout.write(f"\rLast Fetch: {last_fetch} | Updated At: {datetime.fromtimestamp(updated_time).strftime('%Y-%m-%d %H:%M:%S')} | Next API Call: {next_api_call}")
    sys.stdout.flush()

while True:
    latest_fetch_path = latest_fetch()
    with open('config.json', 'r') as file:
        config = json.load(file)
    headers = {
        "User-Agent": USER_AGENT
    }
    ping = requests.get(f'https://dokkan.wiki/api/budokai/{WT_EDITION}', headers=headers)
    # ping.raise_for_status()
    updated_time = datetime.now().timestamp()
    if ping.status_code != 404:
        cond = ping.json()  # Just a "ping" to get the latest rank1000_updated_at

        if latest_fetch_path:
            with open(latest_fetch_path, 'r') as file:
                data = json.load(file)  # Get the latest fetch to see when it has been updated
            if cond["rank1000_updated_at"] != data["rank1000_updated_at"]:  # if it's different then it's updated
                if cond["rank1000_updated_at"] == cond["rank10000_updated_at"]:  # Check if top10k is also updated
                    fetch = fetch_data(size=10000)
                else:
                    fetch = fetch_data(size=1000)

                save_json_to_file(fetch, f"fetch{config['LAST_FETCH']}.json")
                updated_time = cond['rank1000_updated_at']
                config['LAST_FETCH'] += 1
                
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=4)

                try:
                    update_data(fetch, "database.db")
                except Exception as e:
                    print(f"Error: {e}")
        else:
            print("No data, doing first fetch")
            fetch = fetch_data(size=1000)
            save_json_to_file(fetch, f"fetch{config['LAST_FETCH']}.json")
            updated_time = cond['rank1000_updated_at']
            config['LAST_FETCH'] += 1

            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)

            try:
                update_data(fetch, "database.db")
            except Exception as e:
                print(f"Error: {e}")

        # Display dynamic output
        next_api_call = (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')
        dynamic_print(config['LAST_FETCH']-1, updated_time, next_api_call)

    if ping.status_code == 404:
        print("API isn't up yet")

    time.sleep(3 * 60)


#while True:
#    ping = requests.get("https://dokkan.wiki/api/budokai/53")
#    latest_fetch_path = latest_fetch()
#
#    if latest_fetch_path:
#        with open(latest_fetch_path, 'r') as file:
#            data = json.load(file)
#            print("Data loaded from the latest fetch file:")
#    time.sleep(3*60)
