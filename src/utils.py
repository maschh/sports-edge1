from __future__ import annotations
import time, random

def backoff_sleep(attempt: int) -> None:
    time.sleep(min(60, 2 ** attempt + random.random()))
