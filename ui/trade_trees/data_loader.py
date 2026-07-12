import re
import pandas as pd
from datetime import datetime

def parse_date(date_str):
    """Normalizes various date formats into standard YYYY-MM-DD strings."""
    date_str = str(date_str).strip()
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return date_str

def parse_trade_string(trade_str):
    """
    Parses the transaction details to find which players went to which teams.
    Example: "TOR gets: Bradley Zimmer(-0.4) [net 0.1]  |  CLE gets: Anthony Castro(-0.5)"
    Returns a dictionary: { 'TOR': ['Bradley Zimmer'], 'CLE': ['Anthony Castro'] }
    """
    if pd.isna(trade_str):
        return {}
        
    parts = trade_str.split('|')
    team_players = {}
    
    for part in parts:
        part = part.strip()
        # Find the team acronym right before "gets:"
        team_match = re.search(r"([A-Z0-9]+)\s+gets:", part)
        if not team_match:
            continue
        team = team_match.group(1)
        
        # Clean up the string to make player extraction easier
        clean_part = re.sub(r'\[net\s+[^\]]+\]', '', part)  # Remove [net X.X]
        clean_part = re.sub(r'^[A-Z0-9]+\s+gets:\s*', '', clean_part)  # Remove "TEAM gets:"
        
        # Extract players matching the "Player Name(WAR)" format
        players = []
        for player_match in re.finditer(r'([^,]+?)\s*\(-?\d+\.?\d*\)', clean_part):
            player_name = player_match.group(1).strip()
            # Exclude non-player entities like draft picks or cash considerations
            if "cash" not in player_name.lower() and "ptbnl" not in player_name.lower():
                players.append(player_name)
                
        if players:
            team_players[team] = players
            
    return team_players

def load_and_build_tree(csv_path="mlb_trades.csv"):
    """
    Loads the trade CSV, normalizes trade dates, extracts player transactions,
    and returns a relationship dataframe alongside a sorted list of unique players.
    """
    try:
        # Read without a header since your snippet does not include column names
        df = pd.read_csv(csv_path, header=None)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return pd.DataFrame(), []

    relationships = []
    all_players_set = set()

    for _, row in df.iterrows():
        # Match your columns: Date is index 1, Trade breakdown text is the last column (index 8)
        raw_date = row.iloc[1]
        trade_text = row.iloc[-1]
        
        formatted_date = parse_date(raw_date)
        team_assets = parse_trade_string(trade_text)
        
        teams = list(team_assets.keys())
        # Track pairs of players swapped between different teams in the transaction
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team_a_players = team_assets[teams[i]]
                team_b_players = team_assets[teams[j]]
                
                for p_a in team_a_players:
                    for p_b in team_b_players:
                        all_players_set.add(p_a)
                        all_players_set.add(p_b)
                        
                        # In a trade tree context, Player A was swapped for Player B
                        # We build bidirectional edges so your BFS can search upstream/downstream seamlessly
                        relationships.append({'parent_player': p_a, 'player': p_b, 'date': formatted_date})
                        relationships.append({'parent_player': p_b, 'player': p_a, 'date': formatted_date})

    relationship_df = pd.DataFrame(relationships)
    all_players = sorted(list(all_players_set))

    return relationship_df, all_players