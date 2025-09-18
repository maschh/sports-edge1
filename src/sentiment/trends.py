from pytrends.request import TrendReq
import pandas as pd

def trends_by_team(team_names, days: int = 14) -> pd.DataFrame:
    pytrends = TrendReq(hl='en-US', tz=360)
    out = []
    terms = list(team_names)
    for i in range(0, len(terms), 5):
        kw = terms[i:i+5]
        pytrends.build_payload(kw, timeframe=f"now {days}-d", geo="US")
        interest = pytrends.interest_over_time().drop(columns=["isPartial"], errors='ignore')
        if interest.empty: continue
        mean_vals = interest.mean().reset_index()
        mean_vals.columns = ["team", "trends_mean"]
        out.append(mean_vals)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["team","trends_mean"])
