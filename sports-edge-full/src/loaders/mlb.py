import requests, pandas as pd
BASE = "https://statsapi.mlb.com/api/v1"

def load_mlb_results(start_season: int, end_season: int) -> pd.DataFrame:
    frames = []
    for season in range(start_season, end_season + 1):
        url = f"{BASE}/schedule?sportId=1&season={season}"
        r = requests.get(url, timeout=60); r.raise_for_status()
        data = r.json().get("dates", [])
        rows = []
        for d in data:
            for g in d.get("games", []):
                rows.append({
                    "date": g.get("officialDate"),
                    "home": g.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                    "away": g.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                    "home_score": g.get("teams", {}).get("home", {}).get("score"),
                    "away_score": g.get("teams", {}).get("away", {}).get("score"),
                })
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        frames.append(df)
    mlb = pd.concat(frames, ignore_index=True)
    mlb = mlb.dropna(subset=["home_score","away_score"])
    mlb["home_win"] = (mlb["home_score"] > mlb["away_score"]).astype(int)
    return mlb.sort_values("date").reset_index(drop=True)
