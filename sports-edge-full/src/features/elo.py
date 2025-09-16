import pandas as pd

class Elo:
    def __init__(self, k=20, home_advantage=55, base=1500):
        self.k = k; self.home_adv = home_advantage; self.base = base
        self.r = {}
    def rating(self, team): return self.r.get(team, self.base)
    def expect(self, ra, rb): return 1.0 / (1 + 10 ** ((rb - ra)/400))
    def update(self, home, away, home_win):
        ra = self.rating(home) + self.home_adv
        rb = self.rating(away)
        ea = self.expect(ra, rb)
        sa = 1.0 if home_win else 0.0
        delta = self.k * (sa - ea)
        self.r[home] = self.rating(home) + delta
        self.r[away] = self.rating(away) - delta
        return ea

def add_elo(df: pd.DataFrame, home_col='home', away_col='away', result_col='home_win', k=20, home_advantage=55):
    elo = Elo(k=k, home_advantage=home_advantage)
    exps = []
    for _, row in df.iterrows():
        exp = elo.expect(elo.rating(row[home_col])+elo.home_adv, elo.rating(row[away_col]))
        exps.append(exp)
        if result_col in row:
            elo.update(row[home_col], row[away_col], bool(row[result_col]))
    df = df.copy()
    df['elo_home_exp'] = exps
    return df
