"""
Injury features from free sources (CSV driven).

CSV schema (example):
    date,league,team,starters_out,key_players_out,total_out

The function merges on (date, team) and produces features for home/away.
"""
import pandas as pd

def add_injury_features(df: pd.DataFrame, league: str, injuries_csv_path: str | None = None) -> pd.DataFrame:
    df = df.copy()
    cols = ["inj_home_starters_out","inj_home_key_out","inj_home_total_out",
            "inj_away_starters_out","inj_away_key_out","inj_away_total_out"]
    for c in cols:
        df[c] = 0

    if not injuries_csv_path:
        return df

    inj = pd.read_csv(injuries_csv_path, parse_dates=["date"])
    inj = inj[inj["league"].str.upper() == league.upper()].copy()
    inj["date"] = inj["date"].dt.normalize()

    h = inj.rename(columns={
        "team":"home",
        "starters_out":"inj_home_starters_out",
        "key_players_out":"inj_home_key_out",
        "total_out":"inj_home_total_out",
    })
    df = df.merge(h[["date","home","inj_home_starters_out","inj_home_key_out","inj_home_total_out"]],
                  on=["date","home"], how="left")

    a = inj.rename(columns={
        "team":"away",
        "starters_out":"inj_away_starters_out",
        "key_players_out":"inj_away_key_out",
        "total_out":"inj_away_total_out",
    })
    df = df.merge(a[["date","away","inj_away_starters_out","inj_away_key_out","inj_away_total_out"]],
                  on=["date","away"], how="left")

    df[cols] = df[cols].fillna(0).astype(int)
    return df
