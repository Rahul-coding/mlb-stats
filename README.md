# MLB Players stats & daily email

A streamlit application and automated email to track high performaing MLB players, top performances, and visualize trade trees. 

**[Live Stat Comparison App](https://mlbplayersearch.streamlit.app)**

---

## Table of Contents
1. [Features](#-features)
   - [Player Comparison](#1-player-comparison)
   - [Interactive Trade Trees](#2-interactive-trade-trees)
   - [Daily Email Summaries](#3-daily-email-summaries)
2. [How the backend works](#-how-it-works)
3. [Legacy Features](#-legacy-features)

---

## Features

### 1.) Player comparison 
Compare the stats of multiple players for the current MLB season side by side
* **Lookup players** In the sidebar select `Player Comparison` and select either `Batters` or `Pitchers`
* **Comparision** Bars showing how players compare to the rest of the MLB will pop up and the leader in multiple stats will be highlighted in red

### 2.) Interactive Trade Trees
Visualize complex MLB trade relationships as an interactive graph.
* **How to use:** Select `Trade Trees` from the sidebar, choose a player from the dropdown, and adjust the **Max Depth** slider.
* **Interactive UI:** Zoom, drag, and hover over nodes to explore trades.
* **Data source**
  - Trade data is loaded from `ui/trade_trees/mlb_trades.csv`.

### 3.) Daily Email Summaries
A fully automated daily email digest featuring:
* **Stat Leaders:**  Top performers in hitting (HRs, OPS, AVG), starting pitchers (ERA, WHIP, Ks), and relieving categories  (SV+H, WHIP, ERA).
* **Standout Performance:** Uses custom weighted formulas to rank the day's best games:
  * **Hitters:** $+1.5$ per total base, $+1$ per run/RBI, $+0.5$ per walk, $-0.5$ per strikeout.
  * **Pitchers:** $+1.5$ per IP, $+1$ per K, $-2$ per ER, $-0.5$ per BB/H, $+2$ for a Quality Start (otherwise $-1.5$).
* **Dynamic Badges:** Displays a `NEW` badge next to a new category leader, while crossing out the previous leader with a `removed` tag.
* **Top Stories:** Curates the top 5 stories scraped directly from MLB.


---
 
## How It Works 

### Frontend & UI
* **Streamlit:** Serves as the primary web framework, hosting the dashboard.
* **NetworkX & PyVis:** Used by the Trade Trees feature. `networkx` builds the trade graph, `pyvis` generates the interactive HTML visualization, and `streamlit.components.v1` embeds it natively.
* **Data Source:** Trade network data is from [rosternomics.com](https://rosternomics.com).

### Backend & Data Pipelines
* **MLB API & `statsapi`:** The new Player Comparison tool uses the official Python wrapper for the MLB API to pull real-time data, utilizing `pandas` to handle and format the statistical comparisons.
* **Email Automation:** 
  * Powered by `smtplib` and run with **GitHub Actions** automatically every morining.
  * Standings and leader data are fetched via the MLB API.
  * Daily news is parsed from the **MLB RSS Feed** using Python's native `xml.etree.ElementTree`.

---
## ⏳ Legacy Features

<details>
<summary><b>Legacy Player Comparison Tool</b></summary>

The original player comparison tool is kept for educational purposes:
* **How it worked:** You entered player names (e.g., `Ben Rice, Aaron Judge, Chase Burns`), and were prompted to confirm if they were batters (`y`, `n`, or `u`).
* **Technical:** Powered by **Beautiful Soup** to web scrape data directly from player profile pages. 
* **Comparison logic:** Highlighted the best stats (lower ERA/WHIP for pitchers, higher stats for hitters).
</details>
