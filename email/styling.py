from html import escape


def build_html(leaders_data, previous_date=None, categories=None):
    html = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          body {
            margin: 0;
            padding: 24px 12px;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #1f2937;
            line-height: 1.5;
            background: #eef1f5;
          }
          .container {
            max-width: 640px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            border: 1px solid #e2e8f0;
          }
          .header {
            background: #0f2557;
            padding: 28px 32px;
          }
          .header h1 {
            margin: 0;
            color: #ffffff;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 0.02em;
          }
          .header p {
            margin: 6px 0 0;
            color: #b6c2dc;
            font-size: 13px;
          }
          .content {
            padding: 8px 32px 24px;
          }
          .section {
            margin-top: 28px;
          }
          .section-title {
            font-size: 15px;
            font-weight: 700;
            color: #0f2557;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            border-bottom: 2px solid #0f2557;
            padding-bottom: 8px;
            margin-bottom: 4px;
          }
          .category {
            margin-top: 20px;
          }
          .category-title {
            font-size: 14px;
            font-weight: 700;
            color: #334155;
            margin: 0 0 10px;
          }
          table.leaders {
            width: 100%;
            border-collapse: collapse;
          }
          table.leaders tr {
            border-bottom: 1px solid #eef1f5;
          }
          table.leaders tr:last-child {
            border-bottom: none;
          }
          table.leaders td {
            padding: 9px 4px;
            font-size: 14px;
            vertical-align: middle;
          }
          .rank {
            width: 26px;
            color: #94a3b8;
            font-weight: 700;
            font-size: 13px;
          }
          .player-name {
            font-weight: 600;
            color: #0f172a;
          }
          .player-team {
            color: #64748b;
            font-size: 13px;
          }
          .player-value {
            text-align: right;
            font-weight: 700;
            color: #0f2557;
            white-space: nowrap;
          }
          .badge {
            display: inline-block;
            margin-left: 6px;
            padding: 2px 7px;
            border-radius: 999px;
            font-size: 10.5px;
            font-weight: 700;
            letter-spacing: 0.03em;
            vertical-align: middle;
          }
          .new-badge {
            background: #dcfce7;
            color: #15803d;
          }
          .up-badge {
            background: #e0f2fe;
            color: #0369a1;
          }
          .down-badge {
            background: #fee2e2;
            color: #b91c1c;
          }
          .removed-row .player-name,
          .removed-row .player-team,
          .removed-row .player-value {
            color: #b1b8c4;
            text-decoration: line-through;
          }
          .removed-badge {
            background: #f1f5f9;
            color: #94a3b8;
          }
          .footer {
            padding: 20px 32px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            text-align: center;
          }
          .footer a {
            color: #0f2557;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>MLB League Leaders</h1>
    """

    if previous_date:
        html += f'<p>Updated since {escape(str(previous_date))}</p>'

    html += """
          </div>
          <div class="content">
    """

    # Build a mapping from label -> group (hitting/pitching) if categories provided
    label_group = {}
    if categories:
        try:
            for _, (lab, grp) in categories.items():
                label_group[lab] = grp
        except Exception:
            label_group = {}

    # Group labels by their group
    groups = {}
    for label in leaders_data.keys():
        if label.endswith("_removed"):
            continue
        grp = label_group.get(label, "hitting")
        groups.setdefault(grp, []).append(label)

    # render each group separately (e.g., Hitters, Pitchers)
    for grp, labels in groups.items():
        title = "Hitters" if grp == "hitting" else "Pitchers" if grp == "pitching" else grp.title()
        html += f'<div class="section"><div class="section-title">{escape(title)}</div>'

        for label in labels:
            players = leaders_data.get(label, [])
            removed_players = leaders_data.get(f"{label}_removed", [])

            html += f'<div class="category"><div class="category-title">{escape(label)} Leaders</div>'
            html += '<table class="leaders" role="presentation" cellspacing="0" cellpadding="0">'

            for i, player in enumerate(players, start=1):
                new_badge = '<span class="badge new-badge">NEW</span>' if player.get("is_new") else ""
                move_badge = ""
                if player.get("moved_up"):
                    from_rank = player.get("from_rank")
                    to_rank = player.get("to_rank")
                    moved = player.get("moved_up")
                    move_badge = f'<span class="badge up-badge" title="from {from_rank} to {to_rank}">&#9650; {moved}</span>'
                elif player.get("moved_down"):
                    from_rank = player.get("from_rank")
                    to_rank = player.get("to_rank")
                    moved = player.get("moved_down")
                    move_badge = f'<span class="badge down-badge" title="from {from_rank} to {to_rank}">&#9660; {moved + 1}</span>'

                html += f"""
                <tr>
                  <td class="rank">{i}</td>
                  <td>
                    <span class="player-name">{escape(player['name'])}</span>{new_badge}{move_badge}
                    <div class="player-team">{escape(player['team'])}</div>
                  </td>
                  <td class="player-value">{escape(str(player['value']))}</td>
                </tr>
                """

            # render removed players (if any) in the same table with removed styling
            for player in removed_players:
                html += f"""
                <tr class="removed-row">
                  <td class="rank">&mdash;</td>
                  <td>
                    <span class="player-name">{escape(player['name'])}</span><span class="badge removed-badge">REMOVED</span>
                    <div class="player-team">{escape(player['team'])}</div>
                  </td>
                  <td class="player-value">{escape(str(player['value']))}</td>
                </tr>
                """

            html += "</table></div>"

        html += "</div>"

    html += """
          </div>
          <div class="footer">
            <a href="https://mlbstatscompare.streamlit.app/">Compare full baseball stats &rarr;</a>
          </div>
        </div>
      </body>
    </html>
    """

    return html