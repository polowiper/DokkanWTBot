from render import render
import json 
output_dir = 'top100_data'

with open("data.json", "r") as e:
    data = json.load(e)

def top100_players(data):
    u=0
    top100 = []
    for player in data:
        #print(f"{player['name']}: {player['hour'][-1]} -> {player['hour'][-1] == 89.0 and player['ranks'][-1] <= 100}, btw player{u}") 
        u += 1
        if player['hour'][-1] == 89.25 and player['ranks'][-1] <= 100:
            top100.append(player)
    return top100

top100_data = top100_players(data)
i = 0
for player in top100_data:
    print(f"player{i}: {player['name']}")
    i += 1
render(top100_data, output_dir, "all")

#Only run this file at the end of wt if you wanna render every players