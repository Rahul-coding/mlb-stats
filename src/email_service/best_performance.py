from datetime import datetime, timedelta
import pandas as pd
import requests

def get_yesterdays_best_batters():
    #Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Fetching MLB data for: {yesterday}...")

    #get yesterday's schedule
    schedule_url = (
        f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={yesterday}"
    )
    schedule_data = requests.get(schedule_url).json()

    game_pks = []
    for date_obj in schedule_data.get("dates", []):
        for game in date_obj.get("games", []):
            pk = game["gamePk"]
            game_pks.append(game["gamePk"])

    if not game_pks:
        print("No games found for yesterday.")
        return None

    all_batter_stats = []

    #get boxscore data for each game
    for pk in game_pks:
        boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{pk}/boxscore"
        boxscore_data = requests.get(boxscore_url).json()

        # Check both home and away teams
        for team_type in ["home", "away"]:
            team_name = boxscore_data["teams"][team_type]["team"]["name"]
            players = boxscore_data["teams"][team_type]["players"]

            for player_id, player_info in players.items():
                stats = player_info.get("stats", {}).get("batting", {})

                # Only include players who actually had an At-Bat or Plate Appearance
                if stats.get("plateAppearances", 0) > 0:
                    name = player_info["person"]["fullName"]
                    person_id = player_info["person"]["id"]

                    # Extract basic box score stats
                    at_bats = stats.get("atBats", 0)
                    hits = stats.get("hits", 0)
                    rbi = stats.get("rbi", 0)
                    runs = stats.get("runs", 0)
                    home_runs = stats.get("homeRuns", 0)
                    doubles = stats.get("doubles", 0)
                    triples = stats.get("triples", 0)
                    walks = stats.get("baseOnBalls", 0)
                    strike_outs = stats.get("strikeOuts", 0)

                    #calc total bases
                    singles = hits - (doubles + triples + home_runs)
                    total_bases = (
                        singles + (2 * doubles) + (3 * triples) + (4 * home_runs)
                    )

                    # Create a simple "Game Score" value to rank overall impact
                    # (1.5 pt per Total Base, 1pt per Run, 1pt per RBI, 0.5pt per Walk)
                    performance_score = (total_bases * 1.5) + runs + rbi + (walks * 0.5) - strike_outs * 0.5

                    all_batter_stats.append(
                        {
                            "Player": name,
                            "Team": team_name,
                            "AB": at_bats,
                            "H": hits,
                            "Doubles": doubles,
                            "Triples": triples,
                            "HR": home_runs,
                            "RBI": rbi,
                            "R": runs,
                            "BB": walks,
                            "TB": total_bases,
                            "Score": performance_score,
                        }
                    )
                    all_batter_stats.sort(key=lambda x: x["Score"], reverse=True)
    #format the top player info into a DataFrame for better readability
    all_batter_stats_df = pd.DataFrame(all_batter_stats[:3])
    all_batter_stats_df.index += 1  # Start index at 1 for ranking
    all_batter_stats_df = all_batter_stats_df.drop("Score", axis=1)  # Drop the Score column for display
    return all_batter_stats_df

def get_yesterdays_best_pitchers():
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Fetching MLB pitching data for: {yesterday}...")

    # Get yesterday's schedule
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={yesterday}"
    schedule_data = requests.get(schedule_url).json()

    game_pks = []

    for date_obj in schedule_data.get("dates", []):
        for game in date_obj.get("games", []):
            pk = game["gamePk"]
            game_pks.append(game["gamePk"])
    if not game_pks:
        print("No games found for yesterday.")
        return None

    all_pitcher_stats = []

    # Get boxscore data for each game
    for pk in game_pks:
        boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{pk}/boxscore"
        boxscore_data = requests.get(boxscore_url).json()

        for team_type in ["home", "away"]:
            team_name = boxscore_data["teams"][team_type]["team"]["name"]
            players = boxscore_data["teams"][team_type]["players"]

            for player_id, player_info in players.items():
                stats = player_info.get("stats", {}).get("pitching", {})

                # Only include players who pitched
                innings_pitched_str = stats.get("inningsPitched", "0.0")
                if innings_pitched_str != "0.0" and stats.get("battersFaced", 0) > 0:
                    name = player_info["person"]["fullName"]
                    person_id = player_info["person"]["id"]

                    # Extract stats
                    strikeouts = stats.get("strikeOuts", 0)
                    earned_runs = stats.get("earnedRuns", 0)
                    hits = stats.get("hits", 0)
                    walks = stats.get("baseOnBalls", 0)

                    
                    # Convert innings notation (e.g., 5.1) to float decimal for score calculation
                    ip_float = float(innings_pitched_str)

                    #check if pitcher earned the quality start
                    if(ip_float >= 6 and earned_runs <=3):
                        qual_start_score = 2
                    else:
                        qual_start_score = -1.5

                    # Simple Pitcher Game Score Heuristic
                    performance_score = (ip_float * 1.5) + strikeouts - (earned_runs * 2.0) - (walks * 0.5) - (hits * 0.5) + qual_start_score

                    all_pitcher_stats.append({
                        "Player": name,
                        "Team": team_name,
                        "IP": innings_pitched_str,
                        "H": hits,
                        "ER": earned_runs,
                        "BB": walks,
                        "SO": strikeouts,
                        "Score": performance_score
                    })
                    
    all_pitcher_stats.sort(key=lambda x: x["Score"], reverse=True)
    
    # Format top 3 pitchers into a DataFrame
    all_pitcher_stats_df = pd.DataFrame(all_pitcher_stats[:3])
    if not all_pitcher_stats_df.empty:
        all_pitcher_stats_df.index += 1
        all_pitcher_stats_df = all_pitcher_stats_df.drop("Score", axis=1)
    return all_pitcher_stats_df