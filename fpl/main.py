import json
from pathlib import Path

from evaluate_team import select_best_11

def main():
    fpl_dir = Path(__file__).resolve().parent # get the directory containing this script

    with open(fpl_dir / "squad.json", "r", encoding="utf-8") as file: # load current squad
        squad_data = json.load(file)

    with open(fpl_dir / "projected_points.json", "r", encoding="utf-8") as file: # load database of all players and their projected points
        all_players = json.load(file)

    players_by_id = { # create a dictionary for quickly finding players by their id
        player["id"]: player
        for player in all_players["players"]
    }

    squad = squad_data["players"] # get the 15 players from the current squad

    for player in squad: # add predicted points per player of the squad
        player_id = player["id"] # get the players id

        player["points"] = players_by_id[player_id]["gameweeks"][0]["points"] # get the predicted points for that player

    best_11, projected_points, formation = select_best_11(squad) # find best starting 11

    starting_ids = {player["id"] for player in best_11} # create set of starting ids

    bench = [player for player in squad if player["id"] not in starting_ids] # create a list of ids which are on bench

    captain = max(best_11, key=lambda player: player["points"]) # find the captain (highest xp)

    # print the results

    print("\nBest Starting 11:\n")


    print(f"Formation: {formation}\n")

    pitch_width = 80

    player_width = 18

    captain = max(best_11, key=lambda player: player["points"])
    captain_id = captain["id"]


    for position in ["GK", "DEF", "MID", "FWD"]:
        players = [player for player in best_11 if player["position"] == position] # select all players of current position

        names = "".join((f'(C) {player["name"]}' if player["id"] == captain_id else player["name"]).center(player_width) for player in players) # create a row containing the players name

        points = "".join(f'({player["points"] * (2 if player["id"] == captain_id else 1):.2f} pts)'.center(player_width) for player in players)

        print(names.center(pitch_width))
        print(points.center(pitch_width))

    print(f"Total projected points: {projected_points:.2f}")

    print("\nBench:\n")

    for player in bench:
         print(f'{player["position"]}: {player["name"]} ({player["points"]})')

if __name__ == "__main__":
    main()
