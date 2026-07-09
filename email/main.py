import json
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests
from dotenv import load_dotenv

from styling import build_html
from best_performance import get_yesterdays_best_batters


load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENTS = [email.strip() for email in os.getenv("RECIPIENTS", "").split(",") if email.strip()]

url = "https://statsapi.mlb.com/api/v1/stats/leaders"
stats_url = "https://statsapi.mlb.com/api/v1/stats"
SNAPSHOT_FILE = Path(__file__).with_name("daily_leaders_snapshot.json")

# The categories to pull data for.
categories = {
    "homeRuns": ("HR", "hitting"),
    "battingAverage": ("AVG", "hitting"),
    "onBasePlusSlugging": ("OPS", "hitting"),
    # Pitching leaders
    "earnedRunAverage": ("STARTER ERA", "pitching"),
    "whip": ("STARTER WHIP", "pitching"),
    "strikeOuts": ("SO", "pitching")
}

RELIEVER_MIN_IP = 20


def innings_to_float(innings_text):
    """Convert MLB innings notation (e.g. 12.1) into decimal innings."""
    if innings_text is None:
        return 0.0

    innings_str = str(innings_text)
    try:
        whole, _, partial = innings_str.partition(".")
        innings = float(whole or 0)
        if partial == "1":
            innings += 1 / 3
        elif partial == "2":
            innings += 2 / 3
        return innings
    except (TypeError, ValueError):
        return 0.0


def fetch_reliever_leaders(limit=3):
    """Build reliever leaders from season pitching stats.

    MLB leaders endpoint does not expose saves+holds directly, so this computes
    reliever-only rankings from the season stats endpoint.
    """
    params = {
        "stats": "season",
        "group": "pitching",
        "sportIds": 1,
        "playerPool": "all",
        "limit": 2000,
    }
    response = requests.get(stats_url, params=params, timeout=30)
    response.raise_for_status()

    splits = response.json().get("stats", [{}])[0].get("splits", [])

    relievers = []
    for split in splits:
        stat = split.get("stat", {})
        games_started = int(stat.get("gamesStarted") or 0)
        games_played = int(stat.get("gamesPlayed") or 0)

        # Keep relievers only. Starters are handled in the pitching section.
        if games_played <= 0 or games_started > 0:
            continue

        relievers.append(
            {
                "name": split.get("player", {}).get("fullName", "Unknown"),
                "team": split.get("team", {}).get("name", "Unknown Team"),
                "saves": int(stat.get("saves") or 0),
                "holds": int(stat.get("holds") or 0),
                "era": stat.get("era"),
                "whip": stat.get("whip"),
                "innings": innings_to_float(stat.get("inningsPitched")),
            }
        )

    svh = sorted(
        relievers,
        key=lambda p: (p["saves"] + p["holds"], p["saves"]),
        reverse=True,
    )

    ratio_pool = [
        p
        for p in relievers
        if p["innings"] >= RELIEVER_MIN_IP and p["era"] not in (None, "-") and p["whip"] not in (None, "-")
    ]
    era = sorted(ratio_pool, key=lambda p: float(p["era"]))
    whip = sorted(ratio_pool, key=lambda p: float(p["whip"]))

    return {
        "SV+H": [
            {"name": p["name"], "value": str(p["saves"] + p["holds"]), "team": p["team"]}
            for p in svh[:limit]
        ],
        "RELIEVER ERA": [
            {"name": p["name"], "value": str(p["era"]), "team": p["team"]}
            for p in era[:limit]
        ],
        "RELIEVER WHIP": [
            {"name": p["name"], "value": str(p["whip"]), "team": p["team"]}
            for p in whip[:limit]
        ],
    }

def fetch_current_leaders():
    leaders_data = {}

    for category, (label, group) in categories.items():
        params = {
            "leaderCategories": category,
            "statGroup": group,
            "limit": 3
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        leaders = data['leagueLeaders'][0]['leaders']
        leaders_data[label] = [
            {
                "name": player['person']['fullName'],
                "value": player['value'],
                "team": player['team']['name']
            }
            for player in leaders
        ]

    leaders_data.update(fetch_reliever_leaders())

    return leaders_data

def load_previous_snapshot():
    if not SNAPSHOT_FILE.exists():
        return None

    try:
        with SNAPSHOT_FILE.open("r", encoding="utf-8") as snapshot_file:
            return json.load(snapshot_file)
    except (OSError, json.JSONDecodeError):
        return None


def enrich_leaders_with_changes(leaders_data, previous_snapshot):
    previous_leaders = {}
    previous_date = None

    if previous_snapshot:
        previous_leaders = previous_snapshot.get("leaders", {})
        previous_date = previous_snapshot.get("date")

    enriched_leaders = {}

    for label, players in leaders_data.items():
        # current_names and previous players list for comparison
        current_names = {player["name"] for player in players}
        previous_players = previous_leaders.get(label, [])
        previous_names = {player["name"] for player in previous_players}

        # map previous name -> index (0-based rank)
        prev_pos = {player["name"]: idx for idx, player in enumerate(previous_players)}

        enriched_leaders[label] = []
        removed_players = []

        for idx, player in enumerate(players):
            name = player["name"]
            entry = {**player}
            # is_new if not present previously
            entry["is_new"] = bool(previous_names) and name not in previous_names

            # if present previously, compute rank movement
            if name in prev_pos:
                prev_index = prev_pos[name]
                # moved up if previous index > current index (e.g., from 2->1)
                if prev_index > idx:
                    entry["moved_up"] = prev_index - idx
                    entry["from_rank"] = prev_index + 1
                    entry["to_rank"] = idx + 1
                # moved down if previous index < current index (e.g., from 1->2)
                elif prev_index < idx:
                    entry["moved_down"] = idx - prev_index
                    entry["from_rank"] = prev_index + 1
                    entry["to_rank"] = idx + 1
            enriched_leaders[label].append(entry)

        for player in previous_players:
            if player["name"] not in current_names:
                removed_players.append({**player, "is_removed": True})

        if removed_players:
            enriched_leaders[label + "_removed"] = removed_players

    return enriched_leaders, previous_date


def save_snapshot(leaders_data):
    snapshot = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "leaders": leaders_data
    }

    with SNAPSHOT_FILE.open("w", encoding="utf-8") as snapshot_file:
        json.dump(snapshot, snapshot_file, indent=2)
        snapshot_file.write("\n")


leaders_data = fetch_current_leaders()

#get the best performances from yesterday's games and add them to the leaders_data
yesterday_df = get_yesterdays_best_batters()
if yesterday_df is not None and not yesterday_df.empty:
    top_performers = []
    for _, row in yesterday_df.iterrows():
        # Construct a descriptive string of their stat line for the value column
        stat_line = f"{row['H']}-{row['AB']}, {row['HR']} HR, {row['RBI']} RBI, {row['R']} R"
        top_performers.append({
            "name": row["Player"],
            "team": row["Team"],
            "value": stat_line
        })
    # Inject it into leaders_data with a unique label
    leaders_data["YESTERDAY'S TOP PERFORMANCES"] = top_performers

previous_snapshot = load_previous_snapshot()
leaders_with_changes, previous_date = enrich_leaders_with_changes(leaders_data, previous_snapshot)

# Save the current day's leaders so the next run can compare against them.
save_snapshot(leaders_data)

# build the html for the email
html = build_html(leaders_with_changes, previous_date=previous_date, categories=categories)

# Make the actual email.
msg = EmailMessage()
msg['Subject'] = 'MLB League Leaders'
msg['From'] = f"MLB Bot <{EMAIL}>"
msg['To'] = ", ".join(RECIPIENTS)

msg.set_content("Your email client does not support HTML.")
msg.add_alternative(html, subtype='html')

# send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL, APP_PASSWORD)
    smtp.send_message(msg, to_addrs=RECIPIENTS)

print("Email sent!")