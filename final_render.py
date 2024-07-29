from render import render
import json 
output_dir = 'top100_data'

with open("data.json", "r") as e:
    data = json.load(e)

render(data[:3], output_dir, "all")