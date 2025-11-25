import requests
import json


players = requests.get("https://api.sleeper.app/v1/players/nfl").json()

file_to_write = "player_data.json"
with open(file_to_write, 'w') as f:
    json.dump(players, f, indent=2)