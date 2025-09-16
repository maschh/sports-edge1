import pandas as pd
def gdelt_team_tone(team_names, days: int = 14) -> pd.DataFrame:
    # Placeholder to avoid rate-limit errors; returns zeros but keeps interface stable.
    return pd.DataFrame({"team": list(team_names), "tone_mean": 0.0, "tone_n": 0})
