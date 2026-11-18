

def select_best_11(squad):
    formations = [ # define all valid FPL formations
        (3, 4, 3),
        (3, 5, 2),
        (4, 3, 3),
        (4, 4, 2),
        (4, 5, 1),
        (5, 2, 3),
        (5, 3, 2),
        (5, 4, 1),
    ]

    players_by_position = { # group players by position
        "GK": [],
        "DEF": [],
        "MID": [],
        "FWD": [],
    }

    for player in squad: # add each player to the appropriate position list
        players_by_position[player["position"]].append(player)

    for position in players_by_position: # sort each position by expected points, highest first
        players_by_position[position].sort(
            key=lambda player: player["points"],
            reverse=True,
        )

    best_team = None # store the best starting eleven so far

    best_points = float("-inf") # start with really low points total

    for num_def, num_mid, num_fwd in formations: # evaluate each valid formation
        starting_11 = (
            players_by_position["GK"][:1]
            + players_by_position["DEF"][:num_def]
            + players_by_position["MID"][:num_mid]
            + players_by_position["FWD"][:num_fwd]
        )

        total_points = sum(player["points"] for player in starting_11)

        captain = max(starting_11, key=lambda player: player["points"])

        total_points += captain["points"]

        if total_points > best_points:
            best_points = total_points
            best_team = starting_11
            best_formation = (num_def, num_mid, num_fwd)

    return best_team, best_points, best_formation
