from html import escape


def build_html(leaders_data, previous_date=None):
    html = """
    <html>
      <head>
        <style>
          body {
            font-family: Arial, sans-serif;
            color: #0f172a;
            line-height: 1.5;
            background: #f8fafc;
          }
          h2 {
            color: #1e3a8a;
          }
          h3 {
            color: #2563eb;
          }
          ol {
            padding-left: 20px;
          }
          li {
            margin: 5px 0;
          }
          .name {
            font-weight: bold;
          }
          .context {
            margin: 0 0 18px;
            color: #475569;
          }
          .category-note {
            margin: 0 0 8px;
            color: #334155;
            font-size: 0.95rem;
          }
          .new-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            color: #166534;
            font-size: 0.75rem;
            font-weight: bold;
            letter-spacing: 0.02em;
            vertical-align: middle;
          }
          .removed-note {
            margin: 0 0 8px;
            color: #991b1b;
            font-size: 0.95rem;
          }
          .removed-player {
            color: #7f1d1d;
            text-decoration: line-through;
          }
          .removed-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            color: #991b1b;
            font-size: 0.75rem;
            font-weight: bold;
            letter-spacing: 0.02em;
            vertical-align: middle;
          }
        </style>
      </head>
      <body>
        <h2>MLB League Leaders</h2>
    """
    for label, players in leaders_data.items():
        if label.endswith("_removed"):
            continue

        new_players = [player for player in players if player.get("is_new")]
        removed_players = leaders_data.get(f"{label}_removed", [])

        html += f"<h3>{escape(label)} Leaders</h3>"

        if removed_players:
            removed_names = ", ".join(escape(player["name"]) for player in removed_players)

        html += "<ol>"

        for player in players:
            player_class = "new-player" if player.get("is_new") else ""
            new_badge = '<span class="new-badge">NEW</span>' if player.get("is_new") else ""
            html += f"""
            <li class="{player_class}">
              <span class="name">{escape(player['name'])}</span>{new_badge}
              ({escape(player['team'])}) — {escape(str(player['value']))}
            </li>
            """

        html += "</ol>"

        if removed_players:
            for player in removed_players:
                html += f"""
                <li class="removed-player">
                  <span class="name">{escape(player['name'])}</span><span class="removed-badge">REMOVED</span>
                  ({escape(player['team'])}) — {escape(str(player['value']))}
                </li>
                """

            html += "</ol>"

    html += "</body></html>"

    return html