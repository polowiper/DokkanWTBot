import os
import sqlite3
import json
import requests
from datetime import datetime, timezone
from ..config import WT_EDITION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, '../top100_data')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def load_db_data():
    path = os.path.join(BASE_DIR, '../database.db')
    conn = sqlite3.connect(path)
    return conn

def find_player(conn, identifier):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE id = ? OR name = ?", (identifier, identifier))
    row = cursor.fetchone()

    if row is None:
        return None
    player = {description[0]: value for description, value in zip(cursor.description, row)}

    json_fields = ["wins", "points", "ranks", "hour", "points_pace", "wins_pace", "points_wins", "max_points", "max_wins"]

    for field in json_fields:
        if field in player and player[field] is not None:
            try:
                player[field] = json.loads(player[field])
            except json.JSONDecodeError:
                print(f"Error decoding JSON for field {field}. Value: {player[field]}")

    return player

def find_gap(main_player, conn):
    last_hour = main_player["hour"][-1]
    last_rank = main_player["ranks"][-1]
    cursor = conn.cursor()
    conn.create_function("strrev", 1, lambda s: s[::-1])
    cursor.execute("""
        SELECT id FROM players WHERE
        CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2, LENGTH(hour)) AS FLOAT) = ?
            AND
        CAST(SUBSTR(ranks, LENGTH(ranks) - INSTR(strrev(ranks), ',') + 2, LENGTH(ranks)) AS INTEGER) = ?
    """, (last_hour, last_rank+1))
    row = cursor.fetchone()
    if row is None:
        bottom = None
    else:
        bottom_id = row[0]
        bottom = find_player(conn, bottom_id)
    
    cursor.execute("""
        SELECT id FROM players WHERE
        CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2, LENGTH(hour)) AS FLOAT) = ?
            AND
        CAST(SUBSTR(ranks, LENGTH(ranks) - INSTR(strrev(ranks), ',') + 2, LENGTH(ranks)) AS INTEGER) = ?
    """, (last_hour, last_rank-1))
    row = cursor.fetchone()
    if row is None:
        top = None
    else:
        top_id = row[0]
        top = find_player(conn, top_id)
    
    return top, bottom


def load_discord_users():
    path = os.path.join(BASE_DIR, '../discord_users.json')
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({}, f)
    with open(path, 'r') as f:
        return json.load(f)

def save_discord_users(discord_users):
    path = os.path.join(BASE_DIR, '../discord_users.json')
    with open(path, 'w') as f:
        json.dump(discord_users, f, indent=5)

def latest_fetch():
    output_dir = os.path.join(BASE_DIR, "../fetches")
    i = 0
    while True:
        filename = f"fetch{i}.json"
        if not os.path.exists(os.path.join(output_dir, filename)):
            break
        i += 1
    latest_file = os.path.join(output_dir, f"fetch{i-1}.json")
    return latest_file if os.path.exists(latest_file) else None

def time_data():
    latest_fetch_path = latest_fetch()

    if latest_fetch_path:
        with open(latest_fetch_path, 'r') as file:
            data = json.load(file)
            ping = requests.get(f'https://dokkan.wiki/api/budokai/{WT_EDITION}') # API endpoint with necessary API_KEY
            ping.raise_for_status()
            start_end = ping.json()
            start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc) 
            end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc) 
            update = datetime.utcfromtimestamp(data["rank1000_updated_at"]).replace(tzinfo=timezone.utc)
            total = end - start
            left = end - update
            elapsed = update - start
            return update, start, end, total, left, elapsed
    else:
        #print("No fetch files found in the directory.")
        return None, None, None, None, None, None
