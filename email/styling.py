from html import escape

def build_html(leaders_data, previous_date=None, categories=None):
    TEAM_ABBREVIATIONS = {
        "Arizona Diamondbacks": "ARI",
        "Atlanta Braves": "ATL",
        "Baltimore Orioles": "BAL",
        "Boston Red Sox": "BOS",
        "Chicago White Sox": "CWS",
        "Chicago Cubs": "CHC",
        "Cincinnati Reds": "CIN",
        "Cleveland Guardians": "CLE",
        "Colorado Rockies": "COL",
        "Detroit Tigers": "DET",
        "Houston Astros": "HOU",
        "Kansas City Royals": "KC",
        "Los Angeles Angels": "LAA",
        "Los Angeles Dodgers": "LAD",
        "Miami Marlins": "MIA",
        "Milwaukee Brewers": "MIL",
        "Minnesota Twins": "MIN",
        "New York Yankees": "NYY",
        "New York Mets": "NYM",
        "Oakland Athletics": "OAK",
        "Philadelphia Phillies": "PHI",
        "Pittsburgh Pirates": "PIT",
        "San Diego Padres": "SD",
        "San Francisco Giants": "SF",
        "Seattle Mariners": "SEA",
        "St. Louis Cardinals": "STL",
        "Tampa Bay Rays": "TB",
        "Texas Rangers": "TEX",
        "Toronto Blue Jays": "TOR",
        "Washington Nationals": "WSH",
    }
    reliever_labels = {"SV+H", "RELIEVER ERA", "RELIEVER WHIP"}
    display_labels = {
        "STARTER ERA": "ERA",
        "STARTER WHIP": "WHIP",
        "RELIEVER ERA": "ERA",
        "RELIEVER WHIP": "WHIP",
        "YESTERDAY'S BEST BATTERS": "Yesterday's Best Batters",
    }
    font_stack = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;"
    
    html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>MLB League Leaders</title>
      </head>
      <body style="margin: 0; padding: 32px 12px; background-color: #f1f5f9; {font_stack} color: #1e293b;-webkit-font-smoothing: antialiased;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 640px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; border-collapse: separate; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          <tr>
            <td bgcolor="#0A192F" style="padding: 28px 32px; background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);">
              <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: -0.02em; {font_stack}">MLB League Leaders</h1>
    """

    if previous_date:
        html += f'<p style="margin: 6px 0 0; color: #94a3b8; font-size: 13px; font-weight: 500; {font_stack}">Updated since {escape(str(previous_date))}</p>'

    html += """
            </td>
          </tr>
          <tr>
            <td style="padding: 12px 24px 28px;">
    """

    # Group separating logic
    label_group = {}
    if categories:
        try:
            for _, (lab, grp) in categories.items():
                label_group[lab] = grp
        except Exception: pass

    groups = {}
    for label in leaders_data.keys():
        if label.endswith("_removed"): continue
        if label == "YESTERDAY'S BEST BATTERS":
            grp = "standouts"
        else:
            grp = "relieving" if label in reliever_labels else "pitching" if label == "pitching" else label_group.get(label, "hitting")
        groups.setdefault(grp, []).append(label)

    batting_html = ""
    pitching_html = ""

    for grp, labels in groups.items():
        sub_html = ""
        if grp == "hitting": title = "Hitters"
        elif grp == "pitching": title = "Starting Pitchers"
        elif grp == "relieving": title = "Relievers"
        elif grp == "standouts": title = "Yesterday's Best Batters"
        else: title = grp.title()

        sub_html += f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 24px; border-collapse: collapse;">
          <tr>
            <td style="font-size: 13px; font-weight: 800; color: #0A192F; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #0A192F; padding-bottom: 6px; {font_stack}">
              {escape(title)}
            </td>
          </tr>
        </table>
        """

        for label in labels:
            players = leaders_data.get(label, [])
            removed_players = leaders_data.get(f"{label}_removed", [])
            category_label = display_labels.get(label, label)

            sub_html += f"""
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 12px; border-collapse: separate; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
              <tr>
                <td style="font-size: 11px; font-weight: 700; color: #475569; padding: 10px 14px; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; letter-spacing: 0.02em; text-transform: uppercase; {font_stack}">
                  {escape(category_label)}
                </td>
              </tr>
              <tr>
                <td style="padding: 4px 14px 6px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
            """

            # 1. Render Current Leaders
            for i, player in enumerate(players, start=1):
                new_badge = '<span style="background: #e6f4ea; color: #137333; padding: 2px 6px; border-radius: 10px; font-size: 9px; font-weight: 700; margin-left: 6px; display: inline-block; vertical-align: middle;">NEW</span>' if player.get("is_new") else ""
                
                # Check border logic considering if there are removed players coming right after
                is_last = (i == len(players) and not removed_players)
                border_style = "" if is_last else "border-bottom: 1px solid #f1f5f9;"
                player_team = player["team"] 
                team_abbr = TEAM_ABBREVIATIONS.get(player_team, player_team[:3].upper())
                print(TEAM_ABBREVIATIONS.get(player_team))

                sub_html += f"""
                    <tr style="{border_style}">
                      <td width="22" style="padding: 10px 0; font-size: 12px; font-weight: 700; color: #94a3b8; {font_stack}">{i}</td>
                      <td style="padding: 10px 0; font-size: 13px; {font_stack}">
                        <span style="font-weight: 600; color: #0f172a; vertical-align: middle;">{escape(player['name'])}</span>{new_badge}
                        <span style="color: #64748b; font-size: 11px; font-weight: 500; margin-left: 2px;">({escape(team_abbr)})</span>
                      </td>
                      <td align="right" style="padding: 10px 0; font-size: 13px; font-weight: 700; color: #1e3a8a; {font_stack}">{escape(str(player['value']))}</td>
                    </tr>
                """

            # 2. Render Removed Players (If any exist for this category)
            if removed_players:
                removed_badge = '<span style="background: #fce8e6; color: #c5221f; padding: 2px 6px; border-radius: 10px; font-size: 9px; font-weight: 700; margin-left: 6px; display: inline-block; vertical-align: middle; text-decoration: none !important;">REMOVED</span>'
                
                for j, player in enumerate(removed_players):
                    is_last_removed = (j == len(removed_players) - 1)
                    border_style = "" if is_last_removed else "border-bottom: 1px solid #f1f5f9;"
                    player_team = player["team"] 
                    team_abbr = TEAM_ABBREVIATIONS.get(player_team, player_team[:3].upper())

                    sub_html += f"""
                    <tr style="{border_style}">
                      <td width="22" style="padding: 10px 0; font-size: 12px; font-weight: 700; color: #cbd5e1; {font_stack}">&mdash;</td>
                      <td style="padding: 10px 0; font-size: 13px; {font_stack} text-decoration: line-through; color: #94a3b8;">
                        <span style="font-weight: 500; color: #94a3b8; vertical-align: middle;">{escape(player['name'])}</span>
                        <span style="color: #cbd5e1; font-size: 11px; font-weight: 500; margin-left: 2px;">({escape(team_abbr)})</span>
                        {removed_badge}
                      </td>
                      <td align="right" style="padding: 10px 0; font-size: 13px; font-weight: 500; color: #94a3b8; {font_stack} text-decoration: line-through;">{escape(str(player['value']))}</td>
                    </tr>
                    """

            sub_html += "</table></td></tr></table>"
            
        if grp in ["hitting", "standouts"]:
            batting_html += sub_html
        else:
            pitching_html += sub_html

    # Master Layout Wrapper (2 Columns)
    html += f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
          <tr>
            <td width="48%" valign="top" style="width: 48%; min-width: 280px;">
              {batting_html}
            </td>
            <td width="4%" style="width: 4%;">&nbsp;</td>
            <td width="48%" valign="top" style="width: 48%; min-width: 280px;">
              {pitching_html}
            </td>
          </tr>
        </table>
    """

    html += f"""
            </td>
          </tr>
          <tr>
            <td bgcolor="#f8fafc" align="center" style="padding: 24px 32px; border-top: 1px solid #e2e8f0; {font_stack}">
              <a href="https://mlbstatscompare.streamlit.app/" style="color: #1e3a8a; font-size: 13px; font-weight: 700; text-decoration: none; display: inline-block; letter-spacing: -0.01em;">Compare full baseball stats &rarr;</a>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    return html