

def get_transfer_candidates(squad_data, players_by_id, outgoing_id, gameweek):
    selling_price = None
    outgoing_player = players_by_id[outgoing_id]

    for player in squad_data["players"]:
        if player["id"] == outgoing_id:
            selling_price = player["selling_price"]
            position = player["position"]
            break # stop searching once the player is found

    if selling_price is None:
        raise ValueError(f"Outgoing player with id: {outgoing_id}, is not in the current squad!")

    max_affordable_price = squad_data["bank"] + selling_price

    players_with_same_position_and_affordable = {
        player_id: player
        for player_id, player in players_by_id.items()
        if player["position"] == position and player["price"] <= max_affordable_price
    } # dictionary of all players with the same position as the outgoing player and are affordable

    players_sorted_by_points_for_this_gw = dict(
        sorted(
            players_with_same_position_and_affordable.items(),
            key=lambda item: next(
                gw["points"]
                for gw in item[1]["gameweeks"]
                if gw["gw"] == gameweek
            ),
            reverse=True
        )
    )

    return players_sorted_by_points_for_this_gw
