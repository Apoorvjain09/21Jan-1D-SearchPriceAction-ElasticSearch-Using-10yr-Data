# PRD: OHLC Pattern → Historical Date Matcher

## Summary
Build a tool that takes OHLC for 2–10 continuous candles (JSON input with timestamps), converts them to percentage moves, and returns past dates where the same (or similar) percentage pattern occurred. MVP targets NIFTY 50 daily data.

## Problem
Traders want to find historical instances of a price-action pattern without being biased by the absolute index level (e.g., 25k vs 15k). They need a fast way to search for similar percentage moves and get the exact dates.

## Goals
- Accept 2–10 continuous OHLC candles (with `ts`) and return ranked historical dates with matching patterns.
- Normalize patterns as percentages so matches are level-invariant.
- Provide deterministic, fast results on NIFTY 50 daily data.

## Success Metrics
- Precision@10 ≥ 0.8 on a curated validation set of OHLC queries.
- Median query time ≤ 3 seconds on 10+ years of daily data.
- Qualitative user feedback: “matches feel exact.”

## Scope
### In Scope (MVP)
- Direct OHLC JSON input for 2–10 continuous candles.
- Variable candle count N in the input (no fixed length).
- NIFTY 50 daily data only.
- Output top-K dates with similarity scores.

### Out of Scope (MVP)
- Multiple symbols and timeframes.
- Prediction of future outcomes.
- Live market data.

## User Stories
1. As a trader, I input 3–4 candles of OHLC and get dates when similar percentage moves happened in the past.
2. As a researcher, I can switch between 3-candle and 4-candle queries and compare results.
3. As a user, I want to see a similarity score for each matched date.

## Functional Requirements
1. **OHLC Input**
   - Accept a JSON array of 2–10 continuous candles with fields: `ts, open, high, low, close, volume, oi`.
   - Validate ordering and continuity of candles by `ts`.
   - `volume` and `oi` are optional for matching and ignored in MVP.

   **Example input**
   ```json
   [
     {
       "ts": "2026-01-19T09:15:00+05:30",
       "open": 25653.1,
       "high": 25653.3,
       "low": 25494.35,
       "close": 25585.5,
       "volume": 0,
       "oi": 0
     },
     {
       "ts": "2026-01-20T09:15:00+05:30",
       "open": 25580.3,
       "high": 25585.0,
       "low": 25171.35,
       "close": 25232.5,
       "volume": 0,
       "oi": 0
     },
     {
       "ts": "2026-01-21T09:15:00+05:30",
       "open": 25141.0,
       "high": 25300.95,
       "low": 24919.8,
       "close": 25157.5,
       "volume": 0,
       "oi": 0
     }
   ]
   ```

2. **Pattern Normalization**
   - Convert each candle into percentage-based features so patterns are level-invariant.
   - Output a fixed-length vector for the pattern.

3. **Historical Matching**
   - Precompute historical candle vectors from OHLC data.
   - Compare query pattern against historical sequences of length N.
   - Return top-K dates by similarity and filter by a minimum threshold.

4. **Results**
   - List of matched dates (YYYY-MM-DD).
   - Similarity score per date.
   - Output dates correspond to the first candle in each matched historical window.

## Example I/O
**Input**
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

**Output**
```json
[
  { "date": "2018-10-11", "similarity": 0.94 },
  { "date": "2020-03-12", "similarity": 0.91 },
  { "date": "2022-06-13", "similarity": 0.89 }
]
```

## Non-Functional Requirements
- Deterministic results for same input.
- No internet dependency at runtime.
- Modular code to swap matching algorithms.

## Data Requirements
- Historical daily OHLC CSV at `../kaggle-data/NIFTY_50_daily.csv` (relative to `candle-search`) with columns: `date, open, high, low, close, volume`.

## Matching Logic (MVP)
For each candle, compute percentage-based features relative to the candle's open:
- `direction` = sign(close - open)
- `body_pct` = (close - open) / open
- `upper_wick_pct` = (high - max(open, close)) / open
- `lower_wick_pct` = (min(open, close) - low) / open
- `range_pct` = (high - low) / open

Pattern vector is the concatenation of N candles. Similarity can be cosine similarity or Euclidean distance with a direction mismatch penalty.

## Edge Cases
- Missing/zero range candles.
- Non-continuous input candles.
- Extreme outliers (limit via winsorization or clamping).

## Risks & Mitigations
- **False positives**: tighten similarity threshold and add direction penalty.
- **Level bias**: ensure all features are normalized as percentages.
- **User confusion on candle count**: validate input length is 2–10 and return clear errors.
