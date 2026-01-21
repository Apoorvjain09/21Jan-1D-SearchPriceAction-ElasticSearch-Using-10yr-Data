import json
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DEFAULT_HISTORY_PATH = Path("../kaggle-data/NIFTY_50_daily.csv")
DEFAULT_SEARCH_PATH = Path("../candle-search/pattern_search.py")


@st.cache_data
def load_history(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def build_candlestick_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["date"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
            )
        ]
    )
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        height=360,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def window_to_input_json(df: pd.DataFrame) -> str:
    rows = []
    for _, row in df.iterrows():
        ts = row["date"].strftime("%Y-%m-%d") + "T09:15:00+05:30"
        rows.append(
            {
                "ts": ts,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            }
        )
    return json.dumps(rows)


def run_search(search_path: str, history_path: str, input_json: str, top_k: int) -> list:
    cmd = [
        "python3",
        search_path,
        "--input-json",
        input_json,
        "--history",
        history_path,
        "--top-k",
        str(top_k),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Search failed")
    return json.loads(result.stdout)


def main() -> None:
    st.set_page_config(page_title="Candle Search UI", layout="wide")
    st.title("Candle Search UI")

    st.sidebar.header("Data")
    history_path = st.sidebar.text_input("History CSV", str(DEFAULT_HISTORY_PATH))
    search_path = st.sidebar.text_input("Search Script", str(DEFAULT_SEARCH_PATH))

    st.sidebar.header("Query")
    use_json = st.sidebar.checkbox("Search using JSON", value=False)
    candle_count = st.sidebar.slider("Candle count", min_value=2, max_value=10, value=3, step=1, disabled=use_json)
    top_k = st.sidebar.slider("Top K", min_value=1, max_value=50, value=10, step=1)
    json_input = None
    if use_json:
        json_input = st.sidebar.text_area(
            "Input JSON",
            height=200,
            placeholder=(
                "[\n"
                "  {\n"
                "    \"ts\": \"2026-01-19T09:15:00+05:30\",\n"
                "    \"open\": 25653.1,\n"
                "    \"high\": 25653.3,\n"
                "    \"low\": 25494.35,\n"
                "    \"close\": 25585.5\n"
                "  }\n"
                "]"
            ),
        )

    if not Path(history_path).exists():
        st.error(f"History CSV not found: {history_path}")
        st.stop()
    if not Path(search_path).exists():
        st.error(f"Search script not found: {search_path}")
        st.stop()

    df = load_history(history_path)

    if use_json:
        if not json_input or not json_input.strip():
            st.info("Paste input JSON to search.")
            st.stop()
        try:
            json_rows = json.loads(json_input)
            if not isinstance(json_rows, list) or len(json_rows) < 2:
                raise ValueError("Input JSON must be a list with at least 2 candles.")
            window_df = pd.DataFrame(json_rows)
            if not {"ts", "open", "high", "low", "close"}.issubset(window_df.columns):
                raise ValueError("Each candle must include ts, open, high, low, close.")
            window_df["date"] = pd.to_datetime(window_df["ts"], errors="raise").dt.tz_convert(None)
            window_df = window_df[["date", "open", "high", "low", "close"]]
            candle_count = len(window_df)
        except Exception as exc:
            st.error(f"Invalid JSON: {exc}")
            st.stop()
        start_idx = None
    else:
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        start_date = st.sidebar.date_input("Start date", value=max_date, min_value=min_date, max_value=max_date)

        start_dt = pd.to_datetime(start_date)
        idx = df.index[df["date"] == start_dt]
        if len(idx) == 0:
            st.error("Start date not found in history data.")
            st.stop()

        start_idx = int(idx[0])
        end_idx = start_idx + candle_count
        if end_idx > len(df):
            st.error("Not enough candles after the selected start date.")
            st.stop()

        window_df = df.iloc[start_idx:end_idx]

    st.subheader("Selected Window")
    if use_json:
        st.info("Using JSON input for the query window.")
    else:
        chart_df = df.iloc[max(0, start_idx - 100): min(len(df), start_idx + 150)]
        st.plotly_chart(build_candlestick_chart(chart_df, "Context Chart"), use_container_width=True)
    st.dataframe(window_df[["date", "open", "high", "low", "close"]], use_container_width=True)

    if st.button("Search Similar Patterns"):
        input_json = json_input if use_json else window_to_input_json(window_df)
        try:
            results = run_search(search_path, history_path, input_json, top_k=top_k)
        except Exception as exc:
            st.error(str(exc))
            st.stop()

        st.subheader("Matches")
        if not results:
            st.info("No matches found.")
            st.stop()

        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)

        st.subheader("Matched Windows")
        cols = st.columns(2)
        follow_on_candles = 5
        for i, row in results_df.iterrows():
            date_str = row["date"]
            match_idx = df.index[df["date"] == pd.to_datetime(date_str)]
            if len(match_idx) == 0:
                continue
            match_idx = int(match_idx[0])
            match_end = min(len(df), match_idx + candle_count + follow_on_candles)
            match_window = df.iloc[match_idx:match_end]
            title = f"{date_str} (sim {row['similarity']:.3f}, +{follow_on_candles} next)"
            fig = build_candlestick_chart(match_window, title)
            cols[i % 2].plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
