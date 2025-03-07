import sqlite3
import json

def init_db():
    conn = sqlite3.connect("kalis_inferno.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        data TEXT
    )''')
    conn.commit()
    conn.close()

def save_player(player_id, data):
    conn = sqlite3.connect("kalis_inferno.db")
    c = conn.cursor()
    data_json = json.dumps(data)
    c.execute("INSERT OR REPLACE INTO players (player_id, data) VALUES (?, ?)", (player_id, data_json))
    conn.commit()
    conn.close()

def load_player(player_id):
    conn = sqlite3.connect("kalis_inferno.db")
    c = conn.cursor()
    c.execute("SELECT data FROM players WHERE player_id = ?", (player_id,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None
