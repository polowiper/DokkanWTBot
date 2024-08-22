import json 
from datetime import datetime, timezone, timedelta
from render import render

with open("data.json", "r") as e:
    data = json.load(e)
output_dir = "top100_data"
render(data[:3], output_dir, type="bulk",multiple=False,animate=True,  bulk_params=["ranks", "wins", "poiawants", "ranks"])