import json
from pathlib import Path

from .evaluate_team import select_best_11
from .simulate_transfer import simulate_transfer

FPL_DIR = Path(__file__).reslove().parent

def load_data():
    with open(FPL_DIR / "squad.json", encoding="utf-8") as file: # load current squad
        squad_data = json.load(file)

    with open(FPLD_DIR / "projected_points.json", encoding="utf-8") as file:
        predictions = json.load(file)


    players_by_id = {
        player["id"]: player
        for player in predictions["players"]
    }

    return squad_data, players_by_id

def get_current_squad():
    squad_data, _ = load_data() # load latest locally saved squad

    return squad_data

def evaluate_squad(squad_data, players_by_id, gameweek):
    squad = [player.copy() for player in squad_data["players"]] # create separate player dictionaries, leaving the input unchanged

    for player in squad: # attach points for the requested gameweek
        prediction = players_by_id[player["id"]]

        gw_data = next(
            gw for gw in prediction["gameweeks"]
            if gw["gw"] == gameweek
        )

        player["points"] = gw_data["points"]

    best_11, total_points, formation = select_best_11(squad)

    captain = max(best_11, key=lambda p: p["points"])

    return {
        "expected_points": total_points,
        "formation": formation,
        "captain": captain["name"]
        "starting_11": best_11,
    }

def evaluate_transfer(outgoing_id, incoming_id, gameweeek):
    squad_data, players_by_id, = load_data() # load current squad and player database

    current_result = evaluate_squad( # evaluate current squad before making any transfers
        squad_data, players_by_id, gameweek
    )

    new_squad = simulate_transfer( # simulate the transfer
        squad_data,
        players_by_id,
        outgoing_id,
        incoming_id,
    )

    new_result = evaluate_squad( # evaluate the simulated squad after transfer
        new_squad, players_by_id, gameweek
    )

    improvement = (
        new_result["expected_points"] - current_result["expected_points"]
    )

    return {
        "outgoing_id": outgoing_id,
        "incoming_id": incoming_id,
        "gameweek": gameweek,
        "current_expected_points": current_result["expected_points"],
        "new_expected_points": new_result["expected_points"],
        "improvement": improvement,
        "remaining_bank": new_squad["bank"],
        "new_lineup": new_results,
    }
