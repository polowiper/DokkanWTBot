from render import render
import json
import sqlite3
output_dir = 'top100_data'


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

def top100_players(data, latest_hour):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    u=0
    top100 = []
    conn.create_function("strrev", 1, lambda s: s[::-1])
    cursor.execute("""
        SELECT id, CAST (SUBSTR(ranks, LENGTH(ranks) - INSTR(strrev(ranks), ',') + 2, LENGTH(ranks)) AS FLOAT) AS latest_rank FROM players
        WHERE CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2, LENGTH(hour)) AS FLOAT) = ?
        ORDER BY latest_rank DESC
        LIMIT 100
    """)
    cursor.fetchall()
    for row in cursor:
        player = find_player(conn, row[0])
        if player is None:
            continue
        top100.append(player)
    return top100


top100_data = top100_players(data)
i = 0
for player in top100_data:
    print(f"player{i}: {player['name']}")
    i += 1
render(top100_data, output_dir, "all")

#Only run this file at the end of wt if you wanna render every players