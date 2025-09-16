import pandas as pd
from datetime import timedelta
from .train import train_model, FEATURES

def walk_forward(df: pd.DataFrame, initial_days=365, retrain_every_n_days=7):
    df = df.sort_values('date').reset_index(drop=True)
    start_cut = df['date'].min() + pd.Timedelta(days=initial_days)
    cutoff = start_cut
    preds = []
    while cutoff < df['date'].max():
        train = df[df['date'] <= cutoff]
        test = df[(df['date'] > cutoff) & (df['date'] <= cutoff + pd.Timedelta(days=retrain_every_n_days))]
        if len(test) == 0: break
        model, cv = train_model(train)
        proba = model.predict_proba(test[FEATURES].fillna(0.0))[:,1]
        tmp = test[['date','home','away','home_win']].copy()
        tmp['p_home'] = proba
        preds.append(tmp)
        cutoff += pd.Timedelta(days=retrain_every_n_days)
    return pd.concat(preds, ignore_index=True)
