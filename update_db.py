import random
import sqlite3
import json
import os
from datetime import datetime
import os
import json
import requests
from datetime import datetime, timezone, timedelta
import config
#def update(data, fetch):
#    if datetime.utcfromtimestamp(data["userlist"]["updated_at"])

import sqlite3
import json
from datetime import datetime, timezone

def time_data(latest_fetch_path=None):
    if latest_fetch_path == None:
        latest_fetch_path = latest_fetch()

    if latest_fetch_path:
        with open(latest_fetch_path, 'r') as file:
            data = json.load(file)
            ping = requests.get(f'https://dokkan.wiki/api/budokai/{config.WT_EDITION}') # API endpoint with necessary API_KEY
            ping.raise_for_status()
            start_end = ping.json()
            start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc) 
            end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc) 
            update = datetime.utcfromtimestamp(data["rank1000_updated_at"]).replace(tzinfo=timezone.utc)
            total = end - start
            left = end - update
            elapsed = update - start
            #print(f"Update: {update}, Start: {start}, End: {end}, Total: {total}, Left: {left}, Elapsed: {elapsed}")
            return update, start, end, total, left, elapsed
    else:
        #print("No fetch files found in the directory.")
        return None, None, None, None, None, None

def update_json_data_to_db(json_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            wins TEXT,
            points TEXT,
            ranks TEXT,
            hour TEXT,
            points_pace TEXT,
            wins_pace TEXT,
            points_wins TEXT,
            max_points TEXT,
            max_wins TEXT
        )
    ''')
    with open(json_path, 'r') as file:
        json_data = json.load(file)
    i = 0
    for player in json_data:
        #The data format is the same as in the db so we just need to take the player data and insert it into the db players table
        cursor.execute('SELECT * FROM players WHERE id = ?', (player["id"],))
        result = cursor.fetchone()
        if result:
            #Get the current data
            wins = json.loads(result[2])
            points = json.loads(result[3])
            ranks = json.loads(result[4])
            hours = json.loads(result[5])
            points_pace = json.loads(result[6])
            wins_pace = json.loads(result[7])
            points_wins = json.loads(result[8])
            max_points = json.loads(result[9])
            max_wins = json.loads(result[10])
            
            #Update it with the existing data
            wins.append(player["wins"])
            points.append(player["points"])
            ranks.append(player["ranks"])
            hours.append(player["hour"])
            points_pace.append(player["points_pace"])
            wins_pace.append(player["wins_pace"])
            points_wins.append(player["points_wins"])
            max_points.append(player["max_points"])
            max_wins.append(player["max_wins"])

            cursor.execute('''
                UPDATE players SET 
                    wins = ?, points = ?, ranks = ?, hour = ?, points_pace = ?, 
                    wins_pace = ?, points_wins = ?, max_points = ?, max_wins = ?
                WHERE id = ?
            ''', (
                json.dumps(wins), json.dumps(points), json.dumps(ranks), json.dumps(hours), json.dumps(points_pace),
                json.dumps(wins_pace), json.dumps(points_wins), json.dumps(max_points), json.dumps(max_wins), player["id"]
            ))
            i += 1
        else:
            #No player has been found so we need to insert it into the db
            cursor.execute('''
                INSERT INTO players (id, name, wins, points, ranks, hour, points_pace, 
                                     wins_pace, points_wins, max_points, max_wins) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player["id"], player["name"], json.dumps(player["wins"]), json.dumps(player["points"]), 
                json.dumps(player["ranks"]), json.dumps(player["hour"]), json.dumps(player["points_pace"]), 
                json.dumps(player["wins_pace"]), json.dumps(player["points_wins"]), json.dumps(player["max_points"]), json.dumps(player["max_wins"])
            ))
            i += 1
        #print(f"[{i}] Player {player['name']} updated")
    conn.commit()
    conn.close()



def update_data(data_fetch, db_path):
    update = datetime.utcfromtimestamp(data_fetch["rank1000_updated_at"]).replace(tzinfo=timezone.utc)
    ping = requests.get(f'https://dokkan.wiki/api/budokai/{config.WT_EDITION}')
    ping.raise_for_status()
    start_end = ping.json()
    start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc)
    end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc)
    total = end - start
    left = end - update
    #print(f"Start time: {start}, end time: {end}, total time: {total}, left time: {left}, update time: {update}")
    elapsed = update - start

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            wins TEXT,
            points TEXT,
            ranks TEXT,
            hour TEXT,
            points_pace TEXT,
            wins_pace TEXT,
            points_wins TEXT,
            max_points TEXT,
            max_wins TEXT
        )
    ''')

    for ranker in data_fetch["players"]:
        player_id = ranker["id"]
        player_name = ranker["name"]
        player_wins = ranker["win_count"]
        player_points = ranker["points"]
        player_rank = ranker["rank"]
        player_points_wins_ratio = ranker["points"] / ranker["win_count"]

        elapsed_hours = round(elapsed.days * 24 + elapsed.seconds / 3600, 2)

        cursor.execute('SELECT id, name, wins, points, ranks, hour, points_pace, wins_pace, points_wins, max_points, max_wins FROM players WHERE id = ?', (player_id,))
        result = cursor.fetchone()

        if result:
            name = result[1] if result[1] else ""
            wins = json.loads(result[2]) if result[2] else []
            points = json.loads(result[3]) if result[3] else []
            ranks = json.loads(result[4]) if result[4] else []
            hours = json.loads(result[5]) if result[5] else []
            points_pace = json.loads(result[6]) if result[6] else []
            wins_pace = json.loads(result[7]) if result[7] else []
            points_wins = json.loads(result[8]) if result[8] else []
            max_points = json.loads(result[9]) if result[9] else []
            max_wins = json.loads(result[10]) if result[10] else []

            time_delta = elapsed_hours - hours[-1]

            if time_delta == 0:
                continue

            name = player_name
            wins.append(player_wins)
            points.append(player_points)
            ranks.append(player_rank)
            hours.append(elapsed_hours)
    
            if len(hours) <= 5:
                points_pace.append(round(player_points / elapsed_hours, 0))
                wins_pace.append(round(player_wins / elapsed_hours, 2))
            else:
                points_pace.append(round((points[-1] - points[-5]) / (hours[-1] - hours[-5]), 2))
                wins_pace.append(round((wins[-1] - wins[-5]) / (hours[-1] - hours[-5]), 2))

            points_wins.append(player_points_wins_ratio)
            max_points.append(player_points + max(points_pace) * (left.days * 24 + left.seconds / 3600))
            max_wins.append(player_wins + max(wins_pace) * (left.days * 24 + left.seconds / 3600))

            cursor.execute('''
                UPDATE players SET 
                    name = ?, wins = ?, points = ?, ranks = ?, hour = ?, points_pace = ?, 
                    wins_pace = ?, points_wins = ?, max_points = ?, max_wins = ?
                WHERE id = ?
            ''', (
                name, json.dumps(wins), json.dumps(points), json.dumps(ranks), json.dumps(hours), json.dumps(points_pace),
                json.dumps(wins_pace), json.dumps(points_wins), json.dumps(max_points), json.dumps(max_wins), player_id
            ))
        else:
            elapsed_hours = round(elapsed.days * 24 + elapsed.seconds / 3600, 2)
            points_pace = [round(player_points / elapsed_hours, 0)]
            wins_pace = [round(player_wins / elapsed_hours, 2)]
            max_points = [player_points + points_pace[0] * (left.days * 24 + left.seconds / 3600)]
            max_wins = [player_wins + wins_pace[0] * (left.days * 24 + left.seconds / 3600)]

            cursor.execute('''
                INSERT INTO players (id, name, wins, points, ranks, hour, points_pace, 
                                     wins_pace, points_wins, max_points, max_wins) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_id, player_name, json.dumps([player_wins]), json.dumps([player_points]), 
                json.dumps([player_rank]), json.dumps([elapsed_hours]), json.dumps(points_pace), 
                json.dumps(wins_pace), json.dumps([player_points_wins_ratio]), json.dumps(max_points), json.dumps(max_wins)
            ))

    conn.commit()
    conn.close()


#def test_update_data():
#    data = {
#        "players": [
#            {
#                "id": random.randint(0, 10000),
#                "name": f"Polo{random.randint(0, 10000)}",
#                "win_count": random.randint(0, 10000),
#                "points": random.randint(0, 10000),
#                "rank": random.randint(1, 10000)
#            }
#        ],
#        "rank1000_updated_at": int(datetime.now().timestamp())
#    }
#    update_data(data, "database.db")
#
#
#def print_db_content(database_path):
#    conn = sqlite3.connect(database_path)
#    cursor = conn.cursor()
#    cursor.execute("SELECT * FROM players")
#    for row in cursor.fetchall():
#        print(row)
##for i in range(10):
##    test_update_data()
##print_db_content("database.db")
##update_json_data_to_db("data.json", "database.db")
##print_db_content("database.db")
#
##def update_data(data_fetch, ids_path):
##    update = datetime.utcfromtimestamp(data_fetch["rank1000_updated_at"]).replace(tzinfo=timezone.utc) #Yikes the top100 is updated more often than the rest so the assumption that all the data is updated at the same time as the top100 is false LLLL
#    ping = requests.get('https://dokkan.wiki/api/budokai/55')
#    ping.raise_for_status()
#    start_end = ping.json()
#    start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc) 
#    end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc) 
#    total = end - start
#    left = end - update
#    elapsed = update - start
#    try:
#        with open(ids_path, 'r') as file:
#            id_data = json.load(file)
#    except FileNotFoundError:
#        id_data = []
#    id_dict = {player["id"]: player for player in id_data}
#    for ranker in data_fetch["players"]:
#        player_id = ranker["id"]
#        player_name = ranker["name"]
#        player_wins = ranker["win_count"]
#        player_points = ranker["points"]
#        player_rank = ranker["rank"]
#        player_points_wins_ratio = ranker["points"] / ranker["win_count"] 
#
#
#    #Should prob change the player at the top of this comment and the player under this one as the first one is just an iteration and the second one is an acutal dict
#        if player_id in id_dict:
#            '''
#        
#            '''
#            player = id_dict[player_id]
#            wins_delta = player_wins - player["wins"][-1]
#            points_delta = player_points - player["points"][-1]
#            time_delta =  round(elapsed.days * 24 + elapsed.seconds / 3600, 2) - player["hour"][-1]
#            if time_delta == 0:
#                break
#            if wins_delta or points_delta == 0:
#                next
#            player["wins"].append(player_wins)
#            player["points"].append(player_points)
#            player["ranks"].append(player_rank)
#            player["hour"].append(round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2))
#            if len(player["hour"]) <= 5:
#                player["points_pace"].append(round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0))
#                player["wins_pace"].append(round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2))
#            else:
#                player["points_pace"].append(round((player["points"][-1] - player["points"][-5]) / (player["hour"][-1] - player["hour"][-5]), 2))
#                player["wins_pace"].append(round((player["wins"][-1] - player["wins"][-5]) / (player["hour"][-1] - player["hour"][-5]), 2))
#                #print(player["name"] + " | " + str(player["wins_pace"][-1]))
#            player["points_wins"].append(player_points_wins_ratio)
#            player["max_points"].append(player_points + max(player["points_pace"])*(left.days * 24 + left.seconds / 3600))
#            player["max_wins"].append(player_wins + max(player["wins_pace"])*(left.days * 24 + left.seconds / 3600))
#        else:
#            player = {
#                "id": player_id,
#                "name": player_name,
#                "wins": [player_wins],
#                "points": [player_points],
#                "ranks": [player_rank],
#                "hour": [round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2)],
#                "points_pace": [round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0)], #If the user isn't there then we cannot calculate the relative pace so we'll just stick with the average pace
#                "wins_pace": [round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2)],
#                "points_wins": [player_points_wins_ratio],
#                "max_points": [player_points + int(round((player_points)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),0)) * (left.days * 24 + left.seconds / 3600)],
#                "max_wins": [player_wins + int(round((player_wins)/(round(elapsed.days * 24 + elapsed.seconds / 3600,2)),2)) * (left.days * 24 + left.seconds / 3600)]
#            }
#            id_data.append(player)
#    with open(ids_path, 'w') as file:
#            json.dump(id_data, file, indent=5)
    
