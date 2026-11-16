# in this script we ask the fpl server to send us the data, instead of manually looking it up

import requests # allows us to send http requests

url = "https://fantasy.premierleague.com/api/bootstrap-static/"

response = requests.get(url, timeout=15) # send a request to the server
# url: adress where we retrieve the data from
# timeout: waits at max this time for a response
# response is an object that contains the servers reply, reply is in json format

response.raise_for_status() # checks if request was successfull

data = response.json() # convert json into a dictionary

print(data.keys())

players = data["elements"]

players_in_my_team = [
    "Verbruggen",
    "Kinsky",
    "Silva",
    "Calafiori",
    "Gabriel",
    "Konsa",
    "O'Shea",
    "Palmer",
    "Rogers",
    "E.Le Fée",
    "King",
    "Groß",
    "Haaland",
    "N.Jackson",
    "Calvert-Lewin",
]


for player in players:
    if player["web_name"] in players_in_my_team:
        if player["web_name"] == "King" and player["element_type"] == 1:
            continue
        elif player["web_name"] == "Palmer" and player["element_type"] == 1:
            continue
        else:
            print(
                player["id"],
                player["web_name"],
                player["now_cost"]/10
            )

for player in players:
    if player["id"] == 301:
        print("Player with id 301:")
        print(player["web_name"])
    if player["id"] == 542:
        print("Player with id 542:")
        print(player["web_name"])

manager_id = 369005
