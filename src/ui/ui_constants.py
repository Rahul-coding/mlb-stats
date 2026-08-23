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
    .comparison-heading { margin: 2rem 0 1rem; padding-bottom: .75rem; border-bottom: 3px solid #e4572e; }
    .comparison-heading h3 { margin: 0; color: #12304a; letter-spacing: .01em; }
    .comparison-heading p { margin: .3rem 0 0; color: #607080; font-size: .85rem; }
    .player-card { min-height: 330px; padding: 1.25rem 1.15rem 1rem; border: 1px solid #d7e0e6; border-top: 5px solid #12304a; border-radius: 8px; background: linear-gradient(145deg, #ffffff 0%, #f5f8fa 100%); box-shadow: 0 8px 22px rgba(18, 48, 74, .08); }
    .player-card-header { margin-bottom: 1.25rem; padding-bottom: .85rem; border-bottom: 1px solid #dce5ea; }
    .player-card-kicker { margin: 0 0 .2rem; color: #e4572e; font-size: .67rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .player-card-name { margin: 0; color: #12304a; font-size: 1.12rem; font-weight: 800; line-height: 1.2; }
    .stat-container { margin-bottom: 17px; }
    .stat-label { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 7px; color: #355064; font-size: 12px; font-weight: 700; }
    .stat-track { background-color: #dce5ea; border-radius: 10px; width: 100%; height: 10px; position: relative; overflow: visible; }
    .half-mark { position: absolute; left: 50%; top: -3px; width: 2px; height: 16px; background-color: #79909f; z-index: 5; opacity: .75; }
    .stat-bar { height: 100%; border-radius: 10px 0 0 10px; transition: width 0.5s ease-in-out; }
    .stat-bar-label { position: absolute; top: -18px; font-size: 11px; font-weight: 800; white-space: nowrap; text-shadow: 0 1px 0 rgba(0,0,0,0.4); }
    .comparison-table-title { color: #12304a; }
    @media (max-width: 640px) { .player-card { min-height: 0; margin-bottom: 1rem; } }
    </style>
"""