import json
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests
from dotenv import load_dotenv

from styling import build_html

load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENTS = [email.strip() for email in os.getenv("RECIPIENTS", "").split(",") if email.strip()]

url = "https://statsapi.mlb.com/api/v1/stats/leaders"
SNAPSHOT_FILE = Path(__file__).with_name("daily_leaders_snapshot.json")

# The categories to pull data for.
categories = {
    "homeRuns": ("HR", "hitting"),
    "battingAverage": ("AVG", "hitting"),
    "onBasePlusSlugging": ("OPS", "hitting")
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
        current_names = {
            player["name"]
            for player in players
        }
        previous_players = previous_leaders.get(label, [])
        previous_names = {
            player["name"]
            for player in previous_players
        }
        enriched_leaders[label] = []
        removed_players = []

        for player in players:
            enriched_leaders[label].append({
                **player,
                "is_new": bool(previous_names) and player["name"] not in previous_names
            })

        for player in previous_players:
            if player["name"] not in current_names:
                removed_players.append({
                    **player,
                    "is_removed": True
                })

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
previous_snapshot = load_previous_snapshot()
leaders_with_changes, previous_date = enrich_leaders_with_changes(leaders_data, previous_snapshot)

# Save the current day's leaders so the next run can compare against them.
save_snapshot(leaders_data)

# build the html for the email
html = build_html(leaders_with_changes, previous_date=previous_date)

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