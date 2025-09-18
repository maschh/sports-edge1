import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from lightgbm import LGBMClassifier
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

FEATURES = [
    "elo_home_exp",
    "home_form_3","home_form_5","home_form_10",
    "away_form_3","away_form_5","away_form_10",
    "trends_home","trends_away","tone_home","tone_away",
    "inj_home_starters_out","inj_home_key_out","inj_home_total_out",
    "inj_away_starters_out","inj_away_key_out","inj_away_total_out",
    "temp_c","wind_kmh","prcp_mm","is_dome",
]

def train_model(df: pd.DataFrame):
    df = df.dropna(subset=["home_win"])
    for col in FEATURES:
        if col not in df.columns:
            df[col] = 0.0
    X = df[FEATURES].fillna(0.0)
    y = df["home_win"]
    clf = LGBMClassifier(n_estimators=400, learning_rate=0.03, max_depth=-1, subsample=0.8, colsample_bytree=0.8)
    tscv = TimeSeriesSplit(n_splits=5)
    metrics = []
    for tr, te in tscv.split(X):
        clf.fit(X.iloc[tr], y.iloc[tr])
        p = clf.predict_proba(X.iloc[te])[:,1]
        m = {
            "brier": brier_score_loss(y.iloc[te], p),
            "logloss": log_loss(y.iloc[te], p, labels=[0,1]),
            "auc": roc_auc_score(y.iloc[te], p)
        }
        metrics.append(m)
    clf.fit(X, y)
    return clf, pd.DataFrame(metrics)
