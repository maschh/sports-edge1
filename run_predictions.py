import argparse, pandas as pd
from pathlib import Path

from src.loaders.mlb import load_mlb_results
from src.loaders.nba import load_nba_results
from src.loaders.nfl import load_nfl_results
from src.loaders.cfb import load_cfb_results

from src.features.elo import add_elo
from src.features.rolling import add_rolling_form
from src.sentiment.trends import trends_by_team
from src.sentiment.gdelt import gdelt_team_tone
from src.models.backtest import walk_forward
from src.models.totals import totals_walk_forward
from src.render_html import render_html, spread_from_prob
from src.edge.american import prob_to_american, american_str
from src.injuries.features import add_injury_features
from src.weather.meteostat_features import add_weather_features

def enrich(df: pd.DataFrame, league: str, venues_csv: str | None = None, injuries_csv: str | None = None) -> pd.DataFrame:
    df = add_elo(df)
    df = add_rolling_form(df)
    teams = sorted(set(df["home"]) | set(df["away"]))
    trend = trends_by_team(teams, days=14)
    tone = gdelt_team_tone(teams, days=14)
    df = df.merge(trend.rename(columns={"team":"home","trends_mean":"trends_home"}), on="home", how="left")
    df = df.merge(trend.rename(columns={"team":"away","trends_mean":"trends_away"}), on="away", how="left")
    df = df.merge(tone.rename(columns={"team":"home","tone_mean":"tone_home"}), on="home", how="left")
    df = df.merge(tone.rename(columns={"team":"away","tone_mean":"tone_away"}), on="away", how="left")
    df[["trends_home","trends_away","tone_home","tone_away"]] = df[["trends_home","trends_away","tone_home","tone_away"]].fillna(0.0)
    # Injuries (CSV) and Weather (venues CSV)
    if injuries_csv:
        df = add_injury_features(df, league, injuries_csv)
    else:
        df = add_injury_features(df, league, None)
    if venues_csv:
        df = add_weather_features(df, league, venues_csv)
    else:
        df["temp_c"] = None; df["wind_kmh"] = None; df["prcp_mm"] = None; df["is_dome"] = 0
    return df

def main(start: int, end: int, out_path: str, venues_csv: str | None, injuries_csv: str | None):
    leagues = {
        "NFL": load_nfl_results,
        "NBA": load_nba_results,
        "MLB": load_mlb_results,
        "CFB": load_cfb_results,
    }
    pred_rows = []
    for league, loader in leagues.items():
        print(f"[{league}] loading...")
        df = loader(start, end)
        df = enrich(df, league, venues_csv=venues_csv, injuries_csv=injuries_csv)
        print(f"[{league}] walk-forward predicting...")
        wf = walk_forward(df, initial_days=365*2, retrain_every_n_days=7)
        tf = totals_walk_forward(df, initial_days=365*2, retrain_every_n_days=7)
        if wf.empty: continue
        horizon_start = wf["date"].max() - pd.Timedelta(days=14)
        wf_now = wf[wf["date"] >= horizon_start]
        tf_now = tf[tf["date"] >= horizon_start] if not tf.empty else pd.DataFrame(columns=["date","home","away","pred_total"])
        wf_now = wf_now.merge(tf_now, on=["date","home","away"], how="left")

        for _, r in wf_now.iterrows():
            p_home = float(r["p_home"])
            p_away = 1 - p_home
            am_home = prob_to_american(p_home); am_away = prob_to_american(p_away)
            raw_spread = spread_from_prob(p_home, league)
            line_spread = round(raw_spread * 2) / 2.0 if league != "MLB" else (-1.5 if p_home >= 0.5 else +1.5)
            pred_total = float(r["pred_total"]) if pd.notna(r.get("pred_total", float("nan"))) else None

            ml_lean = "HOME" if p_home >= 0.5 else "AWAY"
            if league == "MLB":
                spread_lean = f"{'HOME' if p_home >= 0.5 else 'AWAY'} {'-1.5' if p_home >= 0.5 else '+1.5'}"
            else:
                side = "HOME" if line_spread >= 0 else "AWAY"
                spread_lean = f"{side} {abs(line_spread):.1f}"
            ou_lean = "NO EDGE"
            if pred_total is not None:
                # Simple O/U lean placeholder (needs market line to compare). Keep as NO EDGE unless you have lines.
                ou_lean = "MODEL TOTAL"

            pred_rows.append({
                "Date": pd.to_datetime(r["date"]).strftime("%Y-%m-%d"),
                "League": league,
                "Matchup": f"{r['away']} @ {r['home']}",
                "Home Win Prob": f"{p_home:.1%}",
                "Away Win Prob": f"{p_away:.1%}",
                "Home Price (American)": american_str(am_home),
                "Away Price (American)": american_str(am_away),
                "Pred. Spread (Home−Away)": f"{raw_spread:+.1f}",
                "Model Spread Line": f"{line_spread:+.1f}" if league != "MLB" else ("-1.5" if p_home >= 0.5 else "+1.5"),
                "Pred. Total": f"{pred_total:.1f}" if pred_total is not None else "",
                "Model Lean – ML": ml_lean,
                "Model Lean – Spread": spread_lean,
                "Model Lean – O/U": ou_lean,
            })

    out = Path(out_path)
    print(f"Writing HTML -> {out.resolve()}")
    render_html(pred_rows, out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2019)
    ap.add_argument("--end", type=int, default=2024)
    ap.add_argument("--out", type=str, default="predictions.html")
    ap.add_argument("--venues_csv", type=str, default="data/venues.csv")
    ap.add_argument("--injuries_csv", type=str, default="data/injuries.csv")
    args = ap.parse_args()
    main(args.start, args.end, args.out, args.venues_csv, args.injuries_csv)
