# MLB Stats

## Streamlit UI Navigation
The Streamlit app now includes multiple pages in one interface.

- Use the sidebar `Page` selector to switch between:
  - `Player Comparison`
  - `Trade Trees`

## Player comparison feature (Legacy)
In this feature you can compare the current season stats of multiple players 
- **How to use the app**
  - type the names of the players separated by commas (e.g., `Ben Rice, Aaron Judge, Chase Burns`)
  - You will then be prompted about if each player is a batter or not
  - For the example about you would type  `y, y, n` (if you are unsure type `u`)
- **Compare players**
- You can also compare 2+ players who are all hitters or all pitchers (e.g., `Chase Burns,Paul Skenes`)
  - The player who has the highest stat (ex. avg, ops) will have that stat bolded
  - For stats where lower is better (e.g. `ERA` and `WHIP` the lower stat will be highlighted

## Player comparison feature (New)
In this feature youc an compare the current season stats of multiple players. I chose to
make a new version of this feature as the old one wasn't user friendly and hard to compar stats with
- **How to use this feature**
  - type the names of players separated by commas (e.g. `Ben Rice, Aaron Judge` and press `Lookup Player(s)`
  - If there is more than one hitter/pitcher the player with the higher/better stat will be in red/bolded
  - You can always access the app here: **[MLB stat comparison App](https://mlbstatscompare.streamlit.app)**

## Trade Trees
This page visualizes MLB trade relationships as an interactive directed tree.

- **How to use this feature**
  - Open the Streamlit app and choose `Trade Trees` from the sidebar `Page` selector
  - Select a player from the dropdown
  - Adjust `Max Depth (Generations Away)` in the sidebar to expand or shrink the graph
  - The selected player is highlighted, with ancestors and descendants shown by generation

- **What it uses**
  - `networkx` to build and traverse trade relationships
  - `pyvis` to render the interactive graph
  - `streamlit.components.v1` to embed the generated HTML visualization

- **Data source**
  - Trade data is loaded from `ui/trade_trees/mlb_trades.csv`


## Email Feature
This feature sends a daily email summary of leaders in 3 hitting categories
(*This feature is still very basic and only sends 3 batting categories*)
  - If there is a new leader in a stat a `NEW` badge will be next to their name. The old leader will be crossed out in red
 
**How they work backend**
- **Player Comparison (legacy):** This feature is powered by **Beautiful Soup** for web scraping. The player stats are compared against each other to determine the better stat. *Web scraping was chosen purely for educational purposes* 
- **Player Comparison (new):** The new version uses `streamlit` and the `statsapi` for MLB to pull data. I then use `pandas` to determine the highest/better stat in each column. I found the `statsapi` to be much easier to use than the MLB endpoint
- **Trade Trees:** This feature builds a directed graph of player relationships and renders it as an interactive hierarchical tree using `networkx` + `pyvis` in Streamlit.
- **Email Feature:** This feature utilizes the official **MLB API** to gather data, and uses `smtplib` and **GitHub Actions** to automate the email
