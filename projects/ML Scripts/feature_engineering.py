from preprocessing import rank_to_numeric


def extract_team_features(match_json):

# takes raw Riot match JSON and returns feature dict for ONE match

    participants = match_json["info"]["participants"]

    team1 = participants[:5]
    team2 = participants[5:]

    def aggregate_team(team):
        total_gold = sum(p["goldEarned"] for p in team)
        total_kills = sum(p["kills"] for p in team)
        total_assists = sum(p["assists"] for p in team)
        total_cs = sum(p["totalMinionsKilled"] + p["neutralMinionsKilled"] for p in team)
        total_vision = sum(p["visionScore"] for p in team)

        return {
            "gold": total_gold,
            "kills": total_kills,
            "assists": total_assists,
            "cs": total_cs,
            "vision": total_vision
        }

    t1 = aggregate_team(team1)
    t2 = aggregate_team(team2)

    # Objectives
    team_stats = match_json["info"]["teams"]

    t1_obj = team_stats[0]["objectives"]
    t2_obj = team_stats[1]["objectives"]

    features = {
        "gold_diff": t1["gold"] - t2["gold"],
        "kill_diff": t1["kills"] - t2["kills"],
        "assist_diff": t1["assists"] - t2["assists"],
        "cs_diff": t1["cs"] - t2["cs"],
        "vision_diff": t1["vision"] - t2["vision"],
        "tower_diff": t1_obj["tower"]["kills"] - t2_obj["tower"]["kills"],
        "dragon_diff": t1_obj["dragon"]["kills"] - t2_obj["dragon"]["kills"],
        "baron_diff": t1_obj["baron"]["kills"] - t2_obj["baron"]["kills"],
        "win": 1 if team_stats[0]["win"] else 0
    }

    return features