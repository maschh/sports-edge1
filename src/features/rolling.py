import pandas as pd

def add_rolling_form(df: pd.DataFrame, windows=(3,5,10)):
    frames = []
    for side in ["home","away"]:
        tmp = df[["date", side, "home", "away", "home_win"]].copy()
        tmp["team"] = tmp[side]
        tmp["win"] = tmp["home_win"] if side == "home" else 1 - tmp["home_win"]
        tmp = tmp.sort_values("date")
        for w in windows:
            tmp[f"form_{w}"] = tmp.groupby("team")["win"].rolling(w, min_periods=1).mean().reset_index(0,drop=True)
        tmp = tmp[["date", side] + [f"form_{w}" for w in windows]]
        tmp = tmp.rename(columns={c: f"{side}_{c}" for c in tmp.columns if c.startswith("form_")})
        frames.append(tmp)
    out = df.merge(frames[0], on=["date","home"], how="left")
    out = out.merge(frames[1], on=["date","away"], how="left")
    return out
