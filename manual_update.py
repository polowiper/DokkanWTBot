import json
import os
from update_db import update_data 
#This is a very dirty script to update the data using all the fetch files in case the data.json file is corrupted. Hopefully you won't need it as updating all the data can be quite long especially at the end of WT.

i = 0
while (os.path.exists(f"fetches/fetch{i}.json")):
    with open(f"fetches/fetch{i}.json", 'r') as e:
        data = json.load(e)
    print(f"updating fetch {i}")
    update_data(data, "database.db")
    i += 1
