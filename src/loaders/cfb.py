import pandas as pd

SCHED = "https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/master/schedules/season_schedules.csv.gz"

def load_cfb_results(start_season: int, end_season: int) -> pd.DataFrame:
    df = pd.read_csv(SCHED, compression="infer", low_memory=False)
    df = df[(df["season"] >= start_season) & (df["season"] <= end_season)]
    df = df[df["game_status"] == "Final"]
    df = df.rename(columns={
        "start_date": "date", "home_team": "home", "away_team": "away",
        "home_points": "home_score", "away_points": "away_score"
    })
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
    return df[["date","home","away","home_score","away_score","home_win"]].sort_values("date").reset_index(drop=True)
