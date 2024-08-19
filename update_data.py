import os
import json
import requests
from datetime import datetime, timezone, timedelta

#def update(data, fetch):
#    if datetime.utcfromtimestamp(data["userlist"]["updated_at"])

def update_data(data_fetch, ids_path):
    update = datetime.utcfromtimestamp(data_fetch["rank1000_updated_at"]).replace(tzinfo=timezone.utc) #Yikes the top100 is updated more often than the rest so the assumption that all the data is updated at the same time as the top100 is false LLLL
    ping = requests.get('https://dokkan.wiki/api/budokai/54')
    ping.raise_for_status()
    start_end = ping.json()
    start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc) 
    end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc) 
    total = end - start
    left = end - update
    elapsed = update - start
    try:
        with open(ids_path, 'r') as file:
            id_data = json.load(file)
    except FileNotFoundError:
        id_data = []
    id_dict = {player["id"]: player for player in id_data}
    for ranker in data_fetch["players"]:
        player_id = ranker["id"]
        player_name = ranker["name"]
        player_wins = ranker["win_count"]
        player_points = ranker["points"]
        player_rank = ranker["rank"]
        player_points_wins_ratio = ranker["points"] / ranker["win_count"] 


    #Should prob change the player at the top of this comment and the player under this one as the first one is just an iteration and the second one is an acutal dict
        if player_id in id_dict:
            '''
        
            '''
            player = id_dict[player_id]
            wins_delta = player_wins - player["wins"][-1]
            points_delta = player_points - player["points"][-1]
            time_delta =  round(elapsed.days * 24 + elapsed.seconds / 3600, 2) - player["hour"][-1]
            if time_delta == 0:
                break
            if wins_delta or points_delta == 0:
                next
            player["wins"].append(player_wins)
            player["points"].append(player_points)
            player["ranks"].append(player_rank)
            player["hour"].append(round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2))
            if len(player["hour"]) <= 5:
                player["points_pace"].append(round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0))
                player["wins_pace"].append(round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2))
            else:
                player["points_pace"].append(round((player["points"][-1] - player["points"][-5]) / (player["hour"][-1] - player["hour"][-5]), 2))
                player["wins_pace"].append(round((player["wins"][-1] - player["wins"][-5]) / (player["hour"][-1] - player["hour"][-5]), 2))
                #print(player["name"] + " | " + str(player["wins_pace"][-1]))
            player["points_wins"].append(player_points_wins_ratio)
            player["max_points"].append(player_points + max(player["points_pace"])*(left.days * 24 + left.seconds / 3600))
            player["max_wins"].append(player_wins + max(player["wins_pace"])*(left.days * 24 + left.seconds / 3600))
        else:
            player = {
                "id": player_id,
                "name": player_name,
                "wins": [player_wins],
                "points": [player_points],
                "ranks": [player_rank],
                "hour": [round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2)],
                "points_pace": [round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0)], #If the user isn't there then we cannot calculate the relative pace so we'll just stick with the average pace
                "wins_pace": [round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2)],
                "points_wins": [player_points_wins_ratio],
                "max_points": [player_points + int(round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0)) * (left.days * 24 + left.seconds / 3600)],
                "max_wins": [player_wins + int(round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2)) * (left.days * 24 + left.seconds / 3600)]
            }
            id_data.append(player)
    with open(ids_path, 'w') as file:
            json.dump(id_data, file, indent=5)
    



'''
update = datetime.utcfromtimestamp(data["userlist"]["updated_at"]).replace(tzinfo=timezone.utc)
start = datetime.utcfromtimestamp(data["start_at"]).astimezone(timezone.utc)
end = datetime.utcfromtimestamp(data["end_at"]).astimezone(timezone.utc)
total = end - start
left = end - update
elapsed = update - start 
print(f"""
    Updated at : {update.strftime("%Y-%m-%dT%H:%M:%SZ")}
    Started at : {start.strftime("%Y-%m-%dT%H:%M:%SZ")}
    End at :     {end.strftime("%Y-%m-%dT%H:%M:%SZ")}
    Total time:  {total}
    Time left:   {left}
    Time elapsed:{elapsed}
    Time elapsed (in hours) : {(elapsed.days * 24) + round(elapsed.seconds / 3600, 2)} 
""")
'''
