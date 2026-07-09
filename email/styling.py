from html import escape

def build_html(leaders_data, previous_date=None, categories=None):
    reliever_labels = {"SV+H", "RELIEVER ERA", "RELIEVER WHIP"}
    display_labels = {
        "STARTER ERA": "ERA",
        "STARTER WHIP": "WHIP",
        "RELIEVER ERA": "ERA",
        "RELIEVER WHIP": "WHIP",
        "YESTERDAY'S BEST BATTERS": "Yesterday's Best Batters",
    }
    font_stack = "font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;"
    
    html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>MLB League Leaders</title>
      </head>
      <body style="margin: 0; padding: 24px 12px; background-color: #eef1f5; {font_stack} color: #1f2937;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" max-width="640" style="max-width: 640px; background-color: #ffffff; border: 1px solid #e2e8f0; border-collapse: collapse;">
          <tr>
            <td bgcolor="#0f2557" style="padding: 24px 32px;">
              <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: 0.02em; {font_stack}">MLB League Leaders</h1>
    """

    if previous_date:
        html += f'<p style="margin: 6px 0 0; color: #b6c2dc; font-size: 13px; {font_stack}">Updated since {escape(str(previous_date))}</p>'

    html += """
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 24px 24px;">
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

    # Pre-render the HTML blocks for side-by-side integration
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
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 20px; border-collapse: collapse;">
          <tr>
            <td style="font-size: 14px; font-weight: 700; color: #0f2557; text-transform: uppercase; border-bottom: 3px solid #0f2557; padding-bottom: 4px; {font_stack}">
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
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 12px; border-collapse: collapse; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;">
              <tr>
                <td style="font-size: 12px; font-weight: 700; color: #475569; padding: 8px 12px 4px; background-color: #f1f5f9; {font_stack}">
                  {escape(category_label)}
                </td>
              </tr>
              <tr>
                <td style="padding: 4px 12px 8px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
            """

            for i, player in enumerate(players, start=1):
                new_badge = '<span style="background: #dcfce7; color: #15803d; padding: 1px 4px; border-radius: 4px; font-size: 9px; font-weight: 700; margin-left:4px;">N</span>' if player.get("is_new") else ""
                sub_html += f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                      <td width="18" style="padding: 6px 0; font-size: 12px; font-weight: 700; color: #94a3b8; {font_stack}">{i}</td>
                      <td style="padding: 6px 0; font-size: 13px; {font_stack}">
                        <span style="font-weight: 600; color: #0f172a;">{escape(player['name'])}</span>{new_badge}
                        <span style="color: #64748b; font-size: 11px;">({escape(player['team'][:3].upper())})</span>
                      </td>
                      <td align="right" style="padding: 6px 0; font-size: 13px; font-weight: 700; color: #0f2557; {font_stack}">{escape(str(player['value']))}</td>
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
            <td bgcolor="#f8fafc" align="center" style="padding: 20px 32px; border-top: 1px solid #e2e8f0; {font_stack}">
              <a href="https://mlbstatscompare.streamlit.app/" style="color: #0f2557; font-size: 13px; font-weight: 600; text-decoration: none;">Compare full baseball stats &rarr;</a>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    return html