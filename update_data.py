import os
import json
import requests
from datetime import datetime, timezone, timedelta

#def update(data, fetch):
#    if datetime.utcfromtimestamp(data["userlist"]["updated_at"])

def update_data(data_fetch, ids_path):
    update = datetime.utcfromtimestamp(data_fetch["userlist"]["updated_at"]).replace(tzinfo=timezone.utc)
    start = datetime.fromisoformat(data_fetch["start_at"]).astimezone(timezone.utc)
    end = datetime.fromisoformat(data_fetch["end_at"]).astimezone(timezone.utc)
    total = end - start
    left = end - update
    elapsed = update - start
    try:
        with open(ids_path, 'r') as file:
            id_data = json.load(file)
    except FileNotFoundError:
        id_data = []
    id_dict = {player["id"]: player for player in id_data}
    for ranker in data_fetch["userlist"]["rankers"]:
        player_id = ranker["id"]
        player_name = ranker["name"]
        player_wins = ranker["title_num"]
        player_points = ranker["point"]
        player_rank = ranker["ranking"]
        player_points_wins_ratio = ranker["point"] / ranker["title_num"] 


    #Should prob change the player at the top of this comment and the player under this one as the first one is just an iteration and the second one is an acutal dict
        if player_id in id_dict:
            '''
        
            '''
            player = id_dict[player_id]
            wins_delta = player_wins - player["wins"][-1]
            points_delta = player_points - player["points"][-1]
            time_delta =  round(elapsed.days * 24 + elapsed.seconds / 3600, 2) - player["hour"][-1]
            if wins_delta or points_delta == 0:
                next
            player["wins"].append(player_wins)
            player["points"].append(player_points)
            player["ranks"].append(player_rank)
            player["hour"].append(round(elapsed.days * 24 + elapsed.seconds / 3600,2))
            player["points_pace"].append(round(points_delta / time_delta,0))
            player["wins_pace"].append(round(wins_delta / time_delta,2))
            player["points_wins"].append(player_points_wins_ratio)
        else:
            player = {
                "id": player_id,
                "name": player_name,
                "wins": [player_wins],
                "points": [player_points],
                "ranks": [player_rank],
                "hour": [round(elapsed.days * 24 + elapsed.seconds / 3600,2)],
                "points_pace": [round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0)], #If the user isn't there then we cannot calculate the relative pace so we'll just stick with the average pace
                "wins_pace": [round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2)],
                "points_wins": [player_points_wins_ratio]
            }
            id_data.append(player)
    with open(ids_path, 'w') as file:
            json.dump(id_data, file, indent=4)
    



'''
update = datetime.utcfromtimestamp(data["userlist"]["updated_at"]).replace(tzinfo=timezone.utc)
start = datetime.fromisoformat(data["start_at"]).astimezone(timezone.utc)
end = datetime.fromisoformat(data["end_at"]).astimezone(timezone.utc)
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
#for i in range(0,49):
#    with open(f"fetches/fetch{i}.json", 'r') as e:
#        data = json.load(e)
#    update_data(data, "data.json")