# PRD: Candle Search UI

## Summary
Create a Python UI that loads NIFTY 50 daily data, renders a candlestick chart, lets the user select 2–10 continuous candles, runs the existing search engine in `../candle-search/pattern_search.py`, and displays matching historical dates with a multi‑chart view.

## Goals
- Visual selection of 2–10 candles from a daily chart.
- One‑click search that runs the candle‑search engine without modifying it.
- Clear results table and multi‑chart view for matched dates.

## Scope
### In Scope
- Local UI (Python) using daily OHLC CSV.
- Date‑range selection or candle‑count selection (2–10 candles).
- Run search via subprocess and display results.
- Multi‑chart view of matched windows.

### Out of Scope
- Live data fetching.
- ML‑based pattern detection.
- Any edits to `candle-search` code.

## User Stories
1. As a user, I can pick a start date and candle count (2–10) on a chart and run a search.
2. As a user, I can see top‑K matching dates with similarity scores.
3. As a user, I can open multiple matched windows in a multi‑chart grid to compare patterns.

## Functional Requirements
1. **Data Load**
   - Load daily OHLC from `../kaggle-data/NIFTY_50_daily.csv`.

2. **Chart + Selection**
   - Display a candlestick chart of daily data.
   - Allow selecting a start date and candle count (2–10) to define the query window.

3. **Search Execution**
   - Convert selected window to JSON array format expected by `pattern_search.py`.
   - Execute `../candle-search/pattern_search.py` via subprocess.

4. **Results**
   - Show top‑K matches with similarity scores.
   - Multi‑chart view for each matched window (same candle count).

## Non‑Functional Requirements
- Local‑only operation.
- Deterministic results.
- Clear error messages when files are missing.

## Data Requirements
- Daily OHLC CSV at `../kaggle-data/NIFTY_50_daily.csv`.
- Candle search script at `../candle-search/pattern_search.py`.
