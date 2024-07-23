import json

with open("data.json", "r") as e:
    data = json.load(e)

max_pace = []

for player in data:
    max_pace.append(max(player["wins_pace"]))

print(max(max_pace))
