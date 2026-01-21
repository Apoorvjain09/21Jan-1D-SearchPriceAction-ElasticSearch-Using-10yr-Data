#!/usr/bin/env python3
import argparse
import csv
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple


FEATURE_LEN = 4


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def _direction(open_p: float, close_p: float) -> int:
    if close_p > open_p:
        return 1
    if close_p < open_p:
        return -1
    return 0


def _candle_features(open_p: float, high_p: float, low_p: float, close_p: float) -> Tuple[List[float], int]:
    if open_p == 0:
        raise ValueError("Open price cannot be zero for percentage features.")
    body = (close_p - open_p) / open_p
    upper = (high_p - max(open_p, close_p)) / open_p
    lower = (min(open_p, close_p) - low_p) / open_p
    range_pct = (high_p - low_p) / open_p
    return [body, upper, lower, range_pct], _direction(open_p, close_p)


def _validate_input_candles(candles: List[Dict]) -> None:
    if not (2 <= len(candles) <= 10):
        raise ValueError("Input must contain 2 to 10 candles.")
    ts_list = [_parse_ts(c["ts"]) for c in candles]
    if ts_list != sorted(ts_list):
        raise ValueError("Input candles must be ordered by increasing ts.")


def _features_from_candles(candles: List[Dict]) -> Tuple[List[List[float]], List[int]]:
    feats = []
    dirs = []
    for c in candles:
        f, d = _candle_features(float(c["open"]), float(c["high"]), float(c["low"]), float(c["close"]))
        feats.append(f)
        dirs.append(d)
    return feats, dirs


def _load_history(path: str) -> Tuple[List[str], List[List[float]], List[int]]:
    dates = []
    feats = []
    dirs = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["date"]
            open_p = float(row["open"])
            high_p = float(row["high"])
            low_p = float(row["low"])
            close_p = float(row["close"])
            f_row, d_row = _candle_features(open_p, high_p, low_p, close_p)
            dates.append(date)
            feats.append(f_row)
            dirs.append(d_row)
    return dates, feats, dirs


def _distance(query_feats: List[List[float]], hist_feats: List[List[float]]) -> float:
    total = 0.0
    for i in range(len(query_feats)):
        for j in range(FEATURE_LEN):
            diff = query_feats[i][j] - hist_feats[i][j]
            total += diff * diff
    return math.sqrt(total)


def find_similar_patterns(
    input_candles: List[Dict],
    history_csv_path: str,
    top_k: int = 10,
    min_similarity: float = None,
    direction_penalty: float = 0.1,
) -> List[Dict]:
    _validate_input_candles(input_candles)
    query_feats, query_dirs = _features_from_candles(input_candles)
    dates, feats, dirs = _load_history(history_csv_path)

    n = len(query_feats)
    if len(dates) < n:
        raise ValueError("History is shorter than input pattern length.")

    results = []
    for i in range(0, len(dates) - n + 1):
        window_feats = feats[i : i + n]
        window_dirs = dirs[i : i + n]
        dist = _distance(query_feats, window_feats)
        mismatches = sum(1 for a, b in zip(query_dirs, window_dirs) if a != b)
        dist += mismatches * direction_penalty
        similarity = 1.0 / (1.0 + dist)
        if min_similarity is None or similarity >= min_similarity:
            results.append({"date": dates[i], "similarity": similarity})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def _load_input_candles(input_path: str = None, input_json: str = None) -> List[Dict]:
    if input_json:
        return json.loads(input_json)
    if input_path:
        with open(input_path) as f:
            return json.load(f)
    raise ValueError("Provide --input-file or --input-json.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Find similar historical OHLC patterns.")
    parser.add_argument("--input-file", help="Path to JSON array of candles.")
    parser.add_argument("--input-json", help="JSON array string of candles.")
    parser.add_argument(
        "--history",
        default="kaggle-data/NIFTY_50_daily.csv",
        help="Path to historical daily CSV.",
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--min-similarity", type=float, default=None)
    parser.add_argument("--direction-penalty", type=float, default=0.1)

    args = parser.parse_args()
    candles = _load_input_candles(args.input_file, args.input_json)
    results = find_similar_patterns(
        candles,
        args.history,
        top_k=args.top_k,
        min_similarity=args.min_similarity,
        direction_penalty=args.direction_penalty,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
