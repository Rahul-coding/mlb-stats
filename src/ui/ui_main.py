import streamlit as st
import statsapi
import pandas as pd
import src.ui.search.statcast as statcast 
from src.ui.trade_trees.trade_trees_main import render_trade_trees

# Import our new modules
import src.ui.ui_constants as c
import src.ui.ui_helpers as h

page = st.sidebar.selectbox("Page", ["Player Comparison", "Trade Trees"])
if page == "Trade Trees":
    render_trade_trees()
    st.stop()

hittersStats, pitchersStats = [], []

st.sidebar.button("Info", icon=":material/help:", help="Enter names...")
comparison_mode = st.sidebar.radio("Compare", ["Batters", "Pitchers"])
player = st.text_input("Player Names", placeholder="Aaron Judge, Chase Burns")

if "df_expected" not in st.session_state:
    st.session_state.df_expected = None
if "df_expected_mode" not in st.session_state:
    st.session_state.df_expected_mode = None

if st.session_state.df_expected_mode != comparison_mode:
    st.session_state.df_expected = None

if st.button("Lookup Player(s)"):
    players = [p.strip() for p in player.split(",") if p.strip()]
    
    for player_item in players:
        result = statsapi.lookup_player(player_item)
        if result:
            position = result[0]['primaryPosition']['code']
            playerId = result[0]['id']
            fullName = result[0]['fullName']
            teamName = (statsapi.lookup_team(result[0]['currentTeam']['id']))[0].get('name')

            if comparison_mode == "Pitchers":
                stats = statsapi.player_stat_data(playerId, "pitching", season="2026")
                stats_entries = stats.get('stats', [])
                if not stats_entries or not stats_entries[0].get('stats'):
                    st.write(f"No pitching stats found for '{fullName}'.")
                    continue

                unfilteredStats = stats_entries[0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
                for stat in c.PITCHING_STATS:
                    if stat == "svhd":
                        filteredStats[stat] = unfilteredStats.get('saves', 0) + unfilteredStats.get('holds', 0)
                    else:
                        filteredStats[stat] = unfilteredStats.get(stat, 0)
                pitchersStats.append(filteredStats)
            else: 
                stats = statsapi.player_stat_data(playerId, "hitting", season="2026")
                stats_entries = stats.get('stats', [])
                if not stats_entries or not stats_entries[0].get('stats'):
                    st.write(f"No hitting stats found for '{fullName}'.")
                    continue

                unfilteredStats = stats_entries[0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
                for stat in c.HITTING_STATS:
                    filteredStats[stat] = unfilteredStats.get(stat, "N/A")
                hittersStats.append(filteredStats)
        else:
            st.write(f"Player '{player_item}' not found.")

    if comparison_mode in ["Batters", "Pitchers"]:
        st.session_state.df_expected = statcast.get_stats(players, comparison_mode=comparison_mode)
        st.session_state.df_expected_mode = comparison_mode

# --- Render Standard Tables ---
if hittersStats:
    st.subheader("Hitter Statistics")
    df_hitters = pd.DataFrame(hittersStats)
    df_hitters.index += 1
    if len(hittersStats) > 1:      
        st.dataframe(df_hitters.style.set_properties(**{'text-align': 'center'}).apply(
            lambda col: ['color: red; font-weight: bold' if v == col.max() else '' for v in col], subset=c.HITTING_STATS
        ))
    
if pitchersStats:
    st.subheader("Pitcher Statistics")
    df_pitchers = pd.DataFrame(pitchersStats)
    df_pitchers.index += 1
    if len(pitchersStats) > 1:      
        st.dataframe(df_pitchers.style.set_properties(**{'text-align': 'center'}).apply(
            lambda col: ['color: red; font-weight: bold' if (v == col.max() and col.name not in c.LOWER_BETTER) or (v == col.min() and col.name in c.LOWER_BETTER) else '' for v in col], subset=c.PITCHING_STATS
        ))

# --- Render Savant Visuals ---
df_exp = st.session_state.df_expected
if df_exp is not None and not df_exp.empty:
    st.write("---")
    mode = st.session_state.df_expected_mode
    st.subheader(f"{'Pitcher' if mode == 'Pitchers' else 'Batter'} Statcast Comparison")
    st.markdown(c.SAVANT_CSS, unsafe_allow_html=True)

    # Map the metrics you want to iterate through based on player type
    metric_map = {
        "Pitchers": [("xera", "xERA"), ("xba", "xBA"), ("k_pct", "K%"), ("bb_pct", "BB%")],
        "Batters": [("est_ba", "Expected AVG"), ("est_slg", "Expected SLG"), ("est_woba", "Expected wOBA"), ("brl_percent", "Barrel %")]
    }
    
    cols = st.columns(len(df_exp))
    for idx, (_, row) in enumerate(df_exp.iterrows()):
        with cols[idx]:
            st.markdown(f"### {row.get('player', 'Player')}")
            for key, label in metric_map[mode]:
                val = row.get(key, None)
                pct = h.get_display_pct(val, c.BASELINES.get(key, 1), mode, key=key, df_exp=df_exp)
                color = h.get_stat_color(pct)
                disp = h.format_stat_value(key, val)
                st.markdown(h.render_stat_html(label, disp, pct, color), unsafe_allow_html=True)