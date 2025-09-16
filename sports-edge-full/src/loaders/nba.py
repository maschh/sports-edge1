import requests, pandas as pd
BASE = "https://www.balldontlie.io/api/v1"

def _fetch(endpoint, params):
    out = []; page = 1
    while True:
        r = requests.get(f"{BASE}/{endpoint}", params={**params, "page": page, "per_page": 100}, timeout=60)
        r.raise_for_status(); j = r.json()
        out.extend(j.get("data", []))
        if page >= j.get("meta", {}).get("total_pages", 1): break
        page += 1
    return out

def load_nba_results(start_season: int, end_season: int) -> pd.DataFrame:
    rows = []
    for yr in range(start_season, end_season + 1):
        games = _fetch("games", {"seasons[]": yr})
        for g in games:
            if g.get("status") != "Final": continue
            rows.append({
                "date": g["date"][:10],
                "home": g["home_team"]["full_name"],
                "away": g["visitor_team"]["full_name"],
                "home_score": g["home_team_score"],
                "away_score": g["visitor_team_score"],
            })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
    return df.sort_values("date").reset_index(drop=True)
