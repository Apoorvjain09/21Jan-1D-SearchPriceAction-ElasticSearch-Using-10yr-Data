# Candle Search UI

Local UI to select 2–10 daily candles and search for similar historical patterns using the existing `candle-search` engine.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```

## Paths
Defaults assume this layout:
- History CSV: `../kaggle-data/NIFTY_50_daily.csv`
- Search script: `../candle-search/pattern_search.py`

You can override both in the sidebar.
