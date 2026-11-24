import json
from pathlib import Path

def main():
    fpl_dir = Path(__file__).resolve().parent # get the directory containing this script

    with open(fpl_dir / "projected_points.json", "r", encoding="utf-8") as file:
        players = json.load(file)

    for player in players["players"]:
        if player["name"] == "Doku":
            print(f'{player["name"]} has the id {player["id"]}')

        if player["name"] == "Rogers":
            print(f'{player["name"]} has the id {player["id"]}')

if __name__ == "__main__":
    main()
