# MLB Stats

## Streamlit UI Navigation
The Streamlit app now includes multiple pages in one interface.

- Use the sidebar `Page` selector to switch between:
  - `Player Comparison`
  - `Trade Trees`


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
This feature sends a daily email summary of leaders in many categories
  - **Hitting categories** HRs, OPS, and AVG
  - **Starting Pitcher categories** ERA, WHIP, and Ks
  - **Reliver categories** SV+H, WHIP, and ERA
  - **Top hitting performances** Uses weights of `1.5` per `total base`, `1` per `run`, `1` per `rbi`, `0.5` per `walk` and `-0.5` per `strikeout`
  - **Top pitching perofromances** Uses weights of `1.5` per `inning pitched`, `1` per `strikeout`, `-2` per `Earned run`, `-0.5` per `walk` and `-0.5` per `hit`, `2` if the got the `Quality start` otherwise `-1.5`
  - If there is a new leader in a stat a `NEW` badge will be next to their name. The old leader will be crossed out with a `removed` tag
  - **Top stories** Pulls the first 5 stories from MLB's website
 
**How they work backend**
- **Player Comparison (legacy):** This feature is powered by **Beautiful Soup** for web scraping. The player stats are compared against each other to determine the better stat. *Web scraping was chosen purely for educational purposes* 

-**UI**
- The ui uses `streamlit` to allow the app to allways be accesible. It has to main parts
  - **Player Comparison (new):** The new version uses the `statsapi` for MLB to pull data. I then use `pandas` to determine the highest/better stat in each column. I found the `statsapi` to be much easier to use than the MLB endpoint

  - **Trade Trees:** This feature builds a directed graph of player relationships and renders it as an interactive hierarchical tree using `networkx` + `pyvis` in Streamlit. The CVS file with all of the data was got from **rosternomics.com** 

- **Email Feature:** 
  - **Data collection** This part of the email utilizes the official **MLB API** to gather stats for the top players and standout performances 
  - **Daily email** The email is sent every morning automaticly using `smtplib` and **github actions**
  - **Top stories** The top stories are collected from the **MLB RSS feed** and are parsed using pythons `xml.etree.ElementTree`

