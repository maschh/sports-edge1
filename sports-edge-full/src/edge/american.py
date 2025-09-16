def prob_to_american(p: float) -> int:
    p = min(max(p, 1e-6), 1 - 1e-6)
    if p >= 0.5:
        raw = - (p / (1 - p)) * 100.0
    else:
        raw = ((1 - p) / p) * 100.0
    rounded = int(5 * round(raw / 5))
    if rounded == 0: rounded = 100
    return rounded

def american_str(val: int) -> str:
    return f"+{val}" if val > 0 else f"{val}"
