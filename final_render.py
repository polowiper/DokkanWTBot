from render import render
import json 
output_dir = 'top100_data'

with open("data.json", "r") as e:
    data = json.load(e)

render(data, output_dir, "all")

#Only run this file at the end of wt if you wanna render every players