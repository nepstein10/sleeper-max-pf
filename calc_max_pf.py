import requests
import json
from pprint import pprint

max_points_by_roster = {}
START_OF_PLAYOFFS = 15

with open("player_data.json", 'r') as f:
    players = json.load(f)

with open("taxi_squads.json") as f:
    taxi_squad_removals = json.load(f)

positions = [["QB"], ["RB"], ["RB"], ["WR"], ["WR"], ["TE"], [
    "QB", "WR", "RB", "TE"], ["WR", "RB", "TE"], ["WR", "RB", "TE"], ["DEF"], ["K"]]


def get_league_id():
    print("Fetching league_id via API")
    username = "nepstein10"
    user = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
    leagues = requests.get(
        f"https://api.sleeper.app/v1/user/{user['user_id']}/leagues/nfl/2025").json()
    league = next(l for l in leagues if l["name"] == "Taxi Evasion")
    return league["league_id"]


def get_roster_info(league_id):
    print("Fetching roster info")
    rosters = requests.get(
        f"https://api.sleeper.app/v1/league/{league_id}/rosters").json()
    return rosters


def get_matchups(league_id, week):
    print(f"Fetching matchups for week {week}")
    matchups = requests.get(
        f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}").json()
    return matchups


def max_points(roster_matchup, week, roster):
    matchup_players = [players[p] for p in roster_matchup["players"]]
    for mp in matchup_players:
        mp["points"] = roster_matchup["players_points"][mp["player_id"]]
    matchup_players = list(filter(lambda x: (roster["taxi"] is None or x["player_id"] not in roster["taxi"]) and (
        x["player_id"] not in taxi_squad_removals.keys() or
        taxi_squad_removals[x["player_id"]]["removed"] < week
    ), matchup_players))
    matchup_players.sort(key=lambda x: x["points"], reverse=True)
    points = 0
    for pos in positions:
        player = matchup_players.pop(matchup_players.index(next(p for p in matchup_players if len(
            list(set(p["fantasy_positions"] + pos))) < len(p["fantasy_positions"] + pos))))
        points += player["points"]
    return points


def main():
    known_league_id = "1256102444601970688"
    league_id = known_league_id if known_league_id else get_league_id()

    rosters = get_roster_info(league_id)
    for roster in rosters:
        owner_id = roster["owner_id"]
        user = requests.get(
            f"https://api.sleeper.app/v1/user/{owner_id}").json()
        max_points_by_roster[roster["roster_id"]] = {
            "owner_id": owner_id,
            "username": user["username"],
            "display_name": user["display_name"],
            "points": 0
        }

    for week in range(1, START_OF_PLAYOFFS):
        matchups = get_matchups(league_id, week)
        if matchups == []:
            break
        for matchup in matchups:
            points = max_points(matchup, week, next(
                r for r in rosters if r["roster_id"] == matchup["roster_id"]))
            max_points_by_roster[matchup["roster_id"]]["points"] += points
    
    for mpr in max_points_by_roster.items():
        mpr[1]["points"] = round(mpr[1]["points"], 2)

    max_points_in_order = [(r[1]["display_name"], r[1]["points"]) for r in max_points_by_roster.items()]
    max_points_in_order.sort(key=lambda x: x[1], reverse=True)
    pprint(max_points_in_order)


if __name__ == "__main__":
    main()
