import pandas as pd

SCHED = "https://raw.githubusercontent.com/nflverse/nflfastR-data/master/data/schedules.csv.gz"

def load_nfl_results(start_season: int, end_season: int) -> pd.DataFrame:
    df = pd.read_csv(SCHED, compression="infer")
    df = df[(df["season"] >= start_season) & (df["season"] <= end_season)]
    df = df[df["result"].notna()]
    df = df.rename(columns={
        "game_date": "date", "home_team": "home", "away_team": "away",
        "home_score": "home_score", "away_score": "away_score"
    })
    df["date"] = pd.to_datetime(df["date"])
    df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
    return df[["date","home","away","home_score","away_score","home_win"]].sort_values("date").reset_index(drop=True)
