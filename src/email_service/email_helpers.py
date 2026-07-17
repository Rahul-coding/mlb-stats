import requests
import xml.etree.ElementTree as ET 

RELIEVER_MIN_IP = 20

url = "https://statsapi.mlb.com/api/v1/stats/leaders"
stats_url = "https://statsapi.mlb.com/api/v1/stats"

categories = {
    "homeRuns": ("HR", "hitting"),
    "battingAverage": ("AVG", "hitting"),
    "onBasePlusSlugging": ("OPS", "hitting"),
    # Pitching leaders
    "earnedRunAverage": ("STARTER ERA", "pitching"),
    "whip": ("STARTER WHIP", "pitching"),
    "strikeOuts": ("SO", "pitching")
}

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
    """Build reliever leaders from season pitching stats."""
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

        # Keep relievers only.
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

def fetch_top_stories(limit=5):
    """Fetch top MLB stories from the official RSS feed."""
    feed_url = "https://www.mlb.com/feeds/news/rss.xml"
    try:
        response = requests.get(feed_url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        stories = []
        # XML structure is rss -> channel -> item
        for item in root.findall(".//item")[:limit]:
            title_node = item.find("title")
            link_node = item.find("link")
            
            title = title_node.text if title_node is not None else "MLB Story"
            link = link_node.text if link_node is not None else "https://www.mlb.com"
            
            stories.append({"title": title, "link": link})
        return stories
    except Exception as e:
        print(f"Warning: Could not fetch top stories: {e}")
        return []