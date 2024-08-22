import os
import time
import json
import requests
from datetime import datetime
from update_data import update_data
import config


def save_json_to_file(data, filename):
    with open(f'fetches/{filename}', 'w') as f:
        json.dump(data, f, indent=4)
def latest_fetch():
    output_dir = "fetches"
    i = 0
    while True:
        filename = f"fetch{i}.json"
        if not os.path.exists(os.path.join(output_dir, filename)):
            break
        i += 1
    return f"{output_dir}/fetch{i-1}.json" if os.path.exists(os.path.join(output_dir, f"fetch{i-1}.json")) else None

def fetch_data(size: int=1000):
    headers = {'x-apitoken': config.API_TOKEN}
    response = requests.get(f'https://dokkan.wiki/api/budokai/54/players/live?size={size}', headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    return data

while True:
    latest_fetch_path = latest_fetch()

    ping = requests.get('https://dokkan.wiki/api/budokai/54')
    ping.raise_for_status()
    cond = ping.json() #Just a "ping" to get the latest rank1000_updated_at 
    
    if latest_fetch_path:
        with open(latest_fetch_path, 'r') as file:
            data = json.load(file) #Get the latest fetch to see when it has been updated
        if cond["rank1000_updated_at"] != data["rank1000_updated_at"]: #if it's different then it's updated
            if cond["rank1000_updated_at"] == cond["rank10000_updated_at"]: #We know the data has been updated so if the top10k is the same as the top1k then it means the top10k has been updated as well
                fetch = fetch_data(size=10000)
            else:
                fetch = fetch_data(size=1000)
            save_json_to_file(fetch, f"fetch{config.LAST_FETCH}.json")
            print(f"fetch {config.LAST_FETCH} done.")
            config.LAST_FETCH+=1
    else:
        print("no data, doing first fetch")
        fetch = fetch_data(size=1000)
        save_json_to_file(fetch, f"fetch{config.LAST_FETCH}.json")
        print(f"fetch {config.LAST_FETCH} done.")
        config.LAST_FETCH+=1
    time.sleep(3*60)

data = fetch_data()
print(data)
save_json_to_file(data, "test1.json")

#while True:
#    ping = requests.get("https://dokkan.wiki/api/budokai/53")
#    latest_fetch_path = latest_fetch()
#
#    if latest_fetch_path:
#        with open(latest_fetch_path, 'r') as file:
#            data = json.load(file)
#            print("Data loaded from the latest fetch file:")
#    time.sleep(3*60)
