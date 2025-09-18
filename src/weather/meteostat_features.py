"""
Weather features using free sources.

Primary: Meteostat (no API key) - pip install meteostat
Fallback: NOAA stub / user CSV if needed.

Expected venue CSV schema (user-provided, one row per home team):
    league,team,stadium,lat,lon,dome  # dome: 1 if indoor/closed

Functions:
    add_weather_features(df, league, venues_csv_path) -> df with columns:
        temp_c, wind_kmh, prcp_mm, is_dome
"""
import pandas as pd

def _load_venues(venues_csv_path: str) -> pd.DataFrame:
    ven = pd.read_csv(venues_csv_path)
    req = {"league","team","lat","lon","dome"}
    missing = req - set(ven.columns)
    if missing:
        raise ValueError(f"Venues CSV missing columns: {missing}")
    return ven

def _meteostat_fetch(lat: float, lon: float, date: pd.Timestamp):
    try:
        from meteostat import Hourly, Point
    except Exception:
        return None
    point = Point(lat, lon)
    start = pd.Timestamp(str(pd.to_datetime(date).date()))
    end   = start + pd.Timedelta(days=1)
    try:
        data = Hourly(point, start, end).fetch()
        if data is None or data.empty:
            return None
        out = pd.DataFrame({
            "temp_c": [data["temp"].dropna().mean() if "temp" in data else None],
            "wind_kmh": [data["wspd"].dropna().mean() * 3.6 if "wspd" in data else None],
            "prcp_mm": [data["prcp"].dropna().sum() if "prcp" in data else 0.0],
        })
        return out.iloc[0].to_dict()
    except Exception:
        return None

def add_weather_features(df: pd.DataFrame, league: str, venues_csv_path: str) -> pd.DataFrame:
    ven = _load_venues(venues_csv_path)
    ven = ven[ven["league"].str.upper() == league.upper()].copy()
    df = df.copy()
    df["is_dome"] = 0

    df = df.merge(ven[["team","lat","lon","dome"]].rename(columns={"team":"home"}), on="home", how="left")
    df["is_dome"] = df["dome"].fillna(0).astype(int)
    df.drop(columns=["dome"], inplace=True)

    wx_rows = []
    for _, r in df.iterrows():
        lat = r.get("lat"); lon = r.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            wx_rows.append({"temp_c": None, "wind_kmh": None, "prcp_mm": None})
            continue
        if r["is_dome"] == 1:
            wx_rows.append({"temp_c": 21.0, "wind_kmh": 0.0, "prcp_mm": 0.0})
            continue
        wx = _meteostat_fetch(float(lat), float(lon), pd.to_datetime(r["date"]))
        if wx is None:
            wx_rows.append({"temp_c": None, "wind_kmh": None, "prcp_mm": None})
        else:
            wx_rows.append(wx)

    wx_df = pd.DataFrame(wx_rows)
    df = pd.concat([df.reset_index(drop=True), wx_df], axis=1)
    df.drop(columns=["lat","lon"], inplace=True, errors="ignore")
    return df
