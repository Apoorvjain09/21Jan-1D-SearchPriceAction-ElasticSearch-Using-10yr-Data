# OHLC Pattern Search (NIFTY 50)

Find historical dates where a similar percentage-based price action pattern occurred.

## Input
Provide a JSON array of 2–10 continuous daily candles with fields:
`ts, open, high, low, close` (volume/oi optional and ignored).

Example:
```json
[
  {
    "ts": "2026-01-19T09:15:00+05:30",
    "open": 25653.1,
    "high": 25653.3,
    "low": 25494.35,
    "close": 25585.5
  },
  {
    "ts": "2026-01-20T09:15:00+05:30",
    "open": 25580.3,
    "high": 25585.0,
    "low": 25171.35,
    "close": 25232.5
  },
  {
    "ts": "2026-01-21T09:15:00+05:30",
    "open": 25141.0,
    "high": 25300.95,
    "low": 24919.8,
    "close": 25157.5
  }
]
```

## Run
```bash
cd candle-search 
```
```bash
python3 pattern_search.py --input-file input.json --history ../kaggle-data/NIFTY_50_daily.csv
```

## Options
- `--top-k 10` number of matches to return
- `--min-similarity 0.9` filter weak matches (0–1)
- `--direction-penalty 0.1` penalize direction mismatches
- `--history ../kaggle-data/NIFTY_50_daily.csv` path to daily data
