import pandas as pd
from pathlib import Path
from .edge.american import prob_to_american, american_str

def to_half_point(x: float) -> float:
    return round(x * 2) / 2.0

def spread_from_prob(p_home: float, league: str) -> float:
    edge = (p_home - 0.5)
    if league in ("NFL", "CFB"):
        spread = edge / 0.045
    elif league == "NBA":
        spread = edge / 0.03
    elif league == "MLB":
        spread = edge / 0.15
    else:
        spread = edge / 0.05
    return spread

def render_html(pred_rows, out_path: Path):
    df = pd.DataFrame(pred_rows)
    def style(df: pd.DataFrame) -> str:
        styled = (
            df.style
            .set_table_styles([
                {"selector": "table", "props": [("border-collapse", "separate"), ("border-spacing", "0"), ("width", "100%"), ("font-family", "Inter, Arial, sans-serif"), ("font-size", "14px") ]},
                {"selector": "thead th", "props": [("text-align", "left"), ("background-color", "#f5f7fb"), ("padding", "12px 10px"), ("font-weight", "600"), ("border-bottom", "1px solid #e5e8ef"), ("position","sticky"), ("top","0"), ("z-index","1")]},
                {"selector": "tbody td", "props": [("padding", "10px"), ("border-bottom", "1px solid #f0f2f7")]},
                {"selector": "tbody tr:hover", "props": [("background-color", "#fafbff")]},
                {"selector": "caption", "props": [("caption-side", "top"), ("text-align", "left"), ("font-size", "18px"), ("font-weight", "700"), ("margin", "0 0 8px 0")]},
            ])
            .hide(axis="index")
            .set_caption("Multi‑League Model Predictions (American Odds)")
        )
        return styled.to_html()

    html_table = style(df)
    shell = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Sports Model Predictions</title>
<style>
:root {
  --bg: #ffffff;
  --text: #111827;
  --muted: #4b5563;
  --border: #e5e7eb;
  --chip-bg: #f3f4f6;
}
body { margin: 28px; background: var(--bg); color: var(--text); font-family: Inter, Arial, sans-serif; }
h1 { font-size: 24px; margin: 0 0 12px 0; }
p.summary { margin: 0 0 16px 0; color: var(--muted); }
.codechip { display: inline-block; background: var(--chip-bg); border: 1px solid var(--border); padding: 4px 8px; border-radius: 8px; font-family: ui-monospace, monospace; font-size: 12px; color: #111827; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
</style>
</head>
<body>
  <h1>Sports Model Predictions</h1>
  <p class="summary">
    American odds shown in common book increments (e.g., <span class="codechip">-110</span>, <span class="codechip">+120</span>).
  </p>
  <div class="table-wrap">{table}</div>
</body>
</html>
""".format(table=html_table)
    Path(out_path).write_text(shell, encoding="utf-8")
