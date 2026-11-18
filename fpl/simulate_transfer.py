from copy import deepcopy
from decimal import Decimal

def simulate_transfer(squad_data, players_by_id, outgoing_id, incoming_id):
    new_squad = deepcopy(squad_data) # create a independant copy of the current squad

    squad = new_squad["players"] # get the lst of the 15 players

    outgoing = next(
        (player for player in squad if player["id"] == outgoing_id),
        None,
    )

    if outgoing is None:
        raise ValueError("Outgoing player is not in your squad")

    if any(player["id"] == incoming_id for player in squad):
        raise ValueError("Incoming player is already in your squad")

    incoming = player_by_id[incoming_id]

    if outgoing["position"] != incoming["position"]:
        riase ValueError("Players must have the same position")

    incoming_price = int(Decimal(str(incoming["price"])))

    available_budget = new_squad["bank"] + outgoing["selling_price"]

    if incoming_price > available_budget:
        raise ValueError("Not enough money for this transfer")

    incoming_club = incoming["team"]

    same_club_count = sum(
        players_by_id[player["id"]]["team"] == incoming_club
        for player in squad
        if player["id"] != outgoing_id
    )

    if same_club_count >= 3:
        raise ValueError("Maximum of three players per club exceeded")

    new_player = {
        "id": incoming["id"],
        "name": incoming["name"],
        "position": incoming["position"],
        "current_price": incoming_price,
        "purchase_price": incoming_price,
        "selling_price": incoming_price,
    }

    for index, player in enumerate(squad):
        if player["id"] == outgoing_id:
            squad[index] = new_player
            break

    new_squa["bank"] = available_budget - incoming_price

    return new_squad
