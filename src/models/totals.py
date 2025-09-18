import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error

TOTAL_FEATURES = [
    "elo_home_exp",
    "home_form_3","home_form_5","home_form_10",
    "away_form_3","away_form_5","away_form_10",
    "inj_home_starters_out","inj_home_key_out","inj_home_total_out",
    "inj_away_starters_out","inj_away_key_out","inj_away_total_out",
    "temp_c","wind_kmh","prcp_mm","is_dome",
    "home_pts_for_5","home_pts_against_5",
    "away_pts_for_5","away_pts_against_5",
]

def _add_team_totals_rolling(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_points"] = df["home_score"] + df["away_score"]
    frames = []
    for side in ["home","away"]:
        tmp = df[["date", side, "home", "away", "home_score", "away_score"]].copy()
        tmp["team"] = tmp[side]
        tmp["pts_for"] = tmp["home_score"] if side == "home" else tmp["away_score"]
        tmp["pts_against"] = tmp["away_score"] if side == "home" else tmp["home_score"]
        tmp = tmp.sort_values("date")
        tmp["pts_for_5"] = tmp.groupby("team")["pts_for"].rolling(5, min_periods=1).mean().reset_index(0,drop=True)
        tmp["pts_against_5"] = tmp.groupby("team")["pts_against"].rolling(5, min_periods=1).mean().reset_index(0,drop=True)
        cols = ["date", side, "pts_for_5", "pts_against_5"]
        tmp = tmp[cols].rename(columns={
            "pts_for_5": f"{side}_pts_for_5",
            "pts_against_5": f"{side}_pts_against_5",
        })
        frames.append(tmp)
    out = df.merge(frames[0], on=["date","home"], how="left")
    out = out.merge(frames[1], on=["date","away"], how="left")
    return out

def train_totals_model(df: pd.DataFrame):
    df = _add_team_totals_rolling(df)
    df = df.dropna(subset=["total_points"])
    for col in TOTAL_FEATURES:
        if col not in df.columns:
            df[col] = 0.0
    X = df[TOTAL_FEATURES].fillna(0.0)
    y = df["total_points"]
    reg = LGBMRegressor(n_estimators=400, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8)
    tscv = TimeSeriesSplit(n_splits=5)
    maes = []
    for tr, te in tscv.split(X):
        reg.fit(X.iloc[tr], y.iloc[tr])
        p = reg.predict(X.iloc[te])
        maes.append(mean_absolute_error(y.iloc[te], p))
    reg.fit(X, y)
    return reg, sum(maes)/len(maes)

def totals_walk_forward(df: pd.DataFrame, initial_days=365, retrain_every_n_days=7):
    df = _add_team_totals_rolling(df)
    df = df.sort_values('date').reset_index(drop=True)
    for col in TOTAL_FEATURES:
        if col not in df.columns:
            df[col] = 0.0
    df[TOTAL_FEATURES] = df[TOTAL_FEATURES].fillna(0.0)

    start_cut = df['date'].min() + pd.Timedelta(days=initial_days)
    cutoff = start_cut
    preds = []
    while cutoff < df['date'].max():
        train = df[df['date'] <= cutoff]
        test = df[(df['date'] > cutoff) & (df['date'] <= cutoff + pd.Timedelta(days=retrain_every_n_days))]
        if len(test) == 0: break
        reg, _ = train_totals_model(train)
        yhat = reg.predict(test[TOTAL_FEATURES])
        tmp = test[['date','home','away']].copy()
        tmp['pred_total'] = yhat
        preds.append(tmp)
        cutoff += pd.Timedelta(days=retrain_every_n_days)
    return pd.concat(preds, ignore_index=True)
