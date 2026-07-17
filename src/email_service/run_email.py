import json
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

from email_styling import build_html
from best_performance import get_yesterdays_best_batters, get_yesterdays_best_pitchers
import email_helpers as data_loaders

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# constants
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENTS = [email.strip() for email in os.getenv("RECIPIENTS", "").split(",") if email.strip()]

# FIX: Points to root /data directory relative to this script
SNAPSHOT_FILE = ROOT_DIR / "data" / "daily_leaders_snapshot.json"

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


def load_previous_snapshot():
    if not SNAPSHOT_FILE.exists():
        return None
    try:
        with SNAPSHOT_FILE.open("r", encoding="utf-8") as snapshot_file:
            return json.load(snapshot_file)
    except (OSError, json.JSONDecodeError):
        return None

def save_snapshot(email_data):
    # Ensure the directory exists just in case
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    snapshot = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "leaders": email_data
    }

    with SNAPSHOT_FILE.open("w", encoding="utf-8") as snapshot_file:
        json.dump(snapshot, snapshot_file, indent=2)
        snapshot_file.write("\n")


def enrich_leaders_with_changes(email_data, previous_snapshot):
    previous_leaders = {}
    previous_date = None

    if previous_snapshot:
        previous_leaders = previous_snapshot.get("leaders", {})
        previous_date = previous_snapshot.get("date")

    enriched_leaders = {}

    for label, players in email_data.items():
        current_names = {player["name"] for player in players}
        previous_players = previous_leaders.get(label, [])
        previous_names = {player["name"] for player in previous_players}

        prev_pos = {player["name"]: idx for idx, player in enumerate(previous_players)}

        enriched_leaders[label] = []
        removed_players = []

        for idx, player in enumerate(players):
            name = player["name"]
            entry = {**player}
            entry["is_new"] = bool(previous_names) and name not in previous_names

            if name in prev_pos:
                prev_index = prev_pos[name]
                if prev_index > idx:
                    entry["moved_up"] = prev_index - idx
                    entry["from_rank"] = prev_index + 1
                    entry["to_rank"] = idx + 1
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


email_data = data_loaders.fetch_current_leaders()

# Get the best performances from yesterday's games
yesterday_df = get_yesterdays_best_batters()
if yesterday_df is not None and not yesterday_df.empty:
    top_performers = []
    for _, row in yesterday_df.iterrows():
        stat_line = f"{row['H']}-{row['AB']}, {row['HR']} HR, {row['RBI']} RBI, {row['R']} R"
        top_performers.append({
            "name": row["Player"],
            "team": row["Team"],
            "value": stat_line
        })
    email_data["YESTERDAY'S BEST BATTERS"] = top_performers

# add top pitchers to df
yesterday_pitchers_df = get_yesterdays_best_pitchers()
if yesterday_pitchers_df is not None and not yesterday_pitchers_df.empty:
    top_pitchers = []
    for _, row in yesterday_pitchers_df.iterrows():
        stat_line = f"{row['IP']} IP, {row['H']} H, {row['ER']} ER, {row['SO']} SO"
        top_pitchers.append({"name": row["Player"], "team": row["Team"], "value": stat_line})
    email_data["YESTERDAY'S BEST PITCHERS"] = top_pitchers
    
previous_snapshot = load_previous_snapshot()
leaders_with_changes, previous_date = enrich_leaders_with_changes(email_data, previous_snapshot)

# Save current leaders snapshot
save_snapshot(email_data)

# Fetch current news stories
top_stories = data_loaders.fetch_top_stories(limit=5)

# build HTML (passing the new stories argument)
html = build_html(leaders_with_changes, previous_date=previous_date, categories=categories, stories=top_stories)


# Make the email payload
msg = EmailMessage()
msg['Subject'] = 'MLB League Leaders & Stories'
msg['From'] = f"<{EMAIL}>"
msg['To'] = ", ".join(RECIPIENTS)

msg.set_content("Your email client does not support HTML.")
msg.add_alternative(html, subtype='html')

# FIX: Combined everything into a single secure connection context
print("Connecting to SMTP server...")
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL, APP_PASSWORD)
    smtp.send_message(msg, to_addrs=RECIPIENTS)

print("Email sent!")