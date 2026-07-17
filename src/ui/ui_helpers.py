# helpers.py
import numpy as np
import pandas as pd
from src.ui.ui_constants import MLB_ANCHORS, LOWER_BETTER_KEYS

def get_stat_color(pct):
    if pct < 50:
        fraction = pct / 50
        r = int(0 + fraction * 150)
        g = int(0 + fraction * 175)
        b = int(255 + fraction * -55)
    else:
        r = 255
        g = int((1 - (pct - 50) / 75) * 200)
        b = int((1 - (pct - 50) / 75) * 200)
    return f"rgb({r}, {g}, {b})"

def get_display_pct(value, baseline, mode, key=None, df_exp=None):
    try:
        if value is None: return 0
        val = float(value)
    except Exception:
        return 0

    raw_pct = 0
    if key and key in MLB_ANCHORS:
        try:
            a = MLB_ANCHORS[key]
            if isinstance(a, (list, tuple)) and len(a) == 3:
                amin, amean, amax = float(a[0]), float(a[1]), float(a[2])
                if amax != amin:
                    raw_pct = int(np.interp(val, [amin, amean], [0, 50])) if val <= amean else int(np.interp(val, [amean, amax], [50, 100]))
                else:
                    raw_pct = 50
            elif isinstance(a, (list, tuple)) and len(a) == 2:
                amin, amax = float(a[0]), float(a[1])
                raw_pct = int(np.interp(val, [amin, amax], [0, 100])) if amax != amin else 50
        except Exception:
            pass
    elif key and df_exp is not None and key in df_exp.columns:
        try:
            series = pd.to_numeric(df_exp[key], errors="coerce").dropna()
            if not series.empty:
                smin, smax, smean = float(series.min()), float(series.max()), float(series.mean())
                if smax != smin:
                    raw_pct = int(np.interp(val, [smin, smean], [0, 50])) if val <= smean else int(np.interp(val, [smean, smax], [50, 100]))
                else:
                    raw_pct = 50
        except Exception:
            pass
    else:
        try:
            base = float(baseline) if baseline else 1.0
            raw_pct = min(int((val / base) * 100), 100)
        except Exception:
            pass

    if mode == "Pitchers" and key in LOWER_BETTER_KEYS:
        return 100 - raw_pct
    return raw_pct

def format_stat_value(key, val):
    if val is None: return "N/A"
    if key in ("xera",): return f"{val:.2f}"
    if key in ("est_ba", "est_slg", "est_woba", "xba"): return f".{int(val * 1000)}"
    if key.endswith("_pct"): return f"{val:.1f}%"
    return str(val)

def render_stat_html(label, display_value, pct, color):
    left_pos = max(min(int(pct), 97), 3)
    return f"""
        <div class="stat-container">
            <div class="stat-label">{label}: {display_value}</div>
            <div class="stat-track">
                <div class="stat-bar" style="width: {int(pct)}%; background-color: {color};"></div>
                <div class="stat-bar-label" style="left: {left_pos}%; color: #FFFFFF;">{int(pct)}</div>
                <div class="half-mark"></div>
            </div>
        </div>
    """