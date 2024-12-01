from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "database.db"

def get_random_user():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players ORDER BY RANDOM() LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_identifier(identifier):
    multiple_users = False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try to fetch user by id first
    cursor.execute("SELECT * FROM players WHERE id = ?", (identifier,))
    user = cursor.fetchone()  # fetchall or fetchone doesn't matter here as the id is unique

    # If no result, try to fetch user by name
    if not user:
        # Check if there are multiple users with the same name
        count = cursor.execute("SELECT COUNT(*) FROM players WHERE name = ?", (identifier,)).fetchone()[0]
        
        cursor.execute("SELECT * FROM players WHERE name = ?", (identifier,))        
        if count > 1:
            multiple_users = True
            user = cursor.fetchall()  # Return all the users with the same name
        else:
            user = cursor.fetchone()

    conn.close()
    return user, multiple_users

@app.route('/get-user', methods=['GET'])
def get_user():
    random_flag = request.args.get('random', 'false').lower() == 'true'
    identifier = request.args.get('identifier')

    if random_flag:
        user = get_random_user()
        if not user:
            return jsonify({"error": "No users found in the database."}), 404
        user_data = format_user_data(user)
    else:
        if not identifier:
            return jsonify({"error": "Identifier is required when 'random' is not true."}), 400

        users, multiple_users = get_user_by_identifier(identifier)

        if multiple_users:
            if not users:
                return jsonify({"error": f"No users found with name '{identifier}'."}), 404

            user_data = [format_user_data(user) for user in users]
        else:
            if not users:
                return jsonify({"error": f"No user found with identifier '{identifier}'."}), 404

            user_data = format_user_data(users)

    return jsonify(user_data)


def format_user_data(user):
    # Helper function to format user data into a dictionary
    return {
        "id": user[0],
        "name": user[1],
        "wins": user[2],
        "points": user[3],
        "ranks": user[4],
        "hour": user[5],
        "points_pace": user[6],
        "wins_pace": user[7],
        "points_wins": user[8],
        "max_points": user[9],
        "max_wins": user[10],
    }


if __name__ == '__main__':
    app.run(debug=True)
