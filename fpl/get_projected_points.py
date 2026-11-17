import requests
import json
from pathlib import Path
import datetime

url = "https://fplcopilot.com/api/expected-points?window=10&fresh=1" # FPL copilot API endpoint for the next 10 gameweeks

response = requests.get(url, timeout=15) # request predicted points form the API

print("HTTP status:", response.status_code) # check whether the request was successful

response.raise_for_status() # raise an exception if the API returned an error

players = response.json() # convert the JSON response into python objects

#print(players[0]) # ptint the first players info

projected_data = {
    "latest_update": str(datetime.datetime.now()),
    "source": "FPL Copilot",
    "players": players,
}

output_path = Path(__file__).resolve().parent / "projected_points.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(projected_data, file, indent=4, ensure_ascii=False)

print(f"Saved prediction to {output_path}")
