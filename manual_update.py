import json
from update_data import update_data


for i in range(0,283):
    with open(f"fetches/fetch{i}.json", 'r') as e:
        data = json.load(e)
    update_data(data, "data.json")
