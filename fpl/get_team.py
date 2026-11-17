import requests
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import datetime

# load environment variables

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)

manager_id = 369005

# ==========================================================
# PRIVATE API: Retrieve YOUR FPL team
# ==========================================================

private_url = (
    f"https://fantasy.premierleague.com/api/my-team/{manager_id}")

token = os.getenv("FPL_ACCESS_TOKEN") # read the authentification token

if not token: # check if loaded successfully
    raise ValueError("FPL_ACCESS_TOKEN not found in .env")

# define the headers that Python sends to the FPL server
headers = {
    "X-API-Authorization": token, # send your authentification token to fpl
    "Accept": "application/json", # indicate that we accept JSON data
}

private_response = requests.get(private_url, headers=headers, timeout=15)
print("HTTP status:", private_response.status_code)
private_response.raise_for_status()

my_team_data = private_response.json() # convert python into json objects

#print(data.keys()) # print top level ditionary keys

# to check if it works
"""
for pick in data["picks"]:
    print(
        pick["element"],
        pick["purchase_price"] / 10,
        pick["selling_price"] / 10,
    )

print("Bank:", data["transfers"]["bank"] / 10, "million")
"""

# ==========================================================
# PUBLIC API: Retrieve ALL FPL players
# ==========================================================

public_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

public_response = requests.get(public_url, timeout=15)

public_response.raise_for_status()

fpl_data = public_response.json()



# create a dictionary mapping every FPL player to their infomration

players_by_id = {
    player["id"]: player # key = player ID, value = complete player dictionary
    for player in fpl_data["elements"] # loop through all players from the public API
}

# map fpl position IDs to readable position names

positions = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "FWD",
}

# create the structure that we will eventually save as JSON

squad = {
    "manager_id": manager_id,
    "bank": my_team_data["transfers"]["bank"] / 10,
    "free_transfers": my_team_data["transfers"]["limit"],
    "players": [],
    "latest_update": str(datetime.datetime.now())
}

# loop through each player in current squad

for pick in my_team_data["picks"]:
    player_id = pick["element"] # get the players fpl id

    player = players_by_id[player_id] # find the players details in the public API data

    player_info = {
        "id": player_id,
        "name": player["web_name"],
        "position": positions[player["element_type"]],
        "current_price": player["now_cost"] / 10, # current market price
        "purchase_price": pick["purchase_price"] / 10, # originally paid price
        "selling_price": pick["selling_price"] / 10, # current sell price
    }

    squad["players"].append(player_info) # add the player to our squad list

output_path = Path(__file__).resolve().parent / "squad.json" # define where to save the squad

# open the JSON file in write mode (creates or overwrites the file)
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(squad, file, indent=4, ensure_ascii=False)

print(f"Squad saved to {output_path}")
