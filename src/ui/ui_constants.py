# constants.py

HITTING_STATS = ["gamesPlayed", "runs", "doubles", "triples", "homeRuns", "strikeOuts", "baseOnBalls", "avg", "ops", "stolenBases"]
PITCHING_STATS = ["gamesPlayed", "inningsPitched", "wins", "losses", "baseOnBalls", "strikeOuts", "avg", "era", "whip", "runs", "svhd", "blownSaves"]
LOWER_BETTER = ["era", "whip", "avg"]
LOWER_BETTER_KEYS = {"xera", "xba", "bb_pct"}

BASELINES = {
    "est_ba": 0.360,    
    "est_slg": 0.700,   
    "est_woba": 0.460,  
    "brl_percent": 26.0,
    "xera": 6.5,
    "xba": 0.400,
    "k_pct": 40.0,
    "bb_pct": 15.0,
}

MLB_ANCHORS = {
    "est_ba": [0.150, 0.246, 0.310],
    "est_slg": [0.300, 0.402, 0.575],
    "est_woba": [0.280, 0.320, 0.415],
    "brl_percent": [0.0, 7.0, 17.0],
    "xera": [2.00, 4.00, 6.00],
    "xba": [0.250, 0.320, 0.420],
    "k_pct": [0.0, 20.0, 50.0],
    "bb_pct": [0.0, 8.0, 20.0],
}

SAVANT_CSS = """
    <style>
    .stat-container { margin-bottom: 15px; }
    .stat-label { font-size: 14px; font-weight: bold; margin-bottom: 4px; }
    .stat-track { background-color: #e0e0e0; border-radius: 10px; width: 100%; height: 12px; position: relative; overflow: visible; }
    .half-mark { position: absolute; left: 50%; top: -3px; width: 2px; height: 18px; background-color: #333333; z-index: 5; opacity: 0.8; }
    @media (prefers-color-scheme: dark) { .half-mark { background-color: #FFFFFF; } }
    .stat-bar { height: 100%; border-radius: 10px 0 0 10px; transition: width 0.5s ease-in-out; }
    .stat-bar-label { position: absolute; top: -18px; font-size: 12px; font-weight: 700; white-space: nowrap; text-shadow: 0 1px 0 rgba(0,0,0,0.4); }
    </style>
"""