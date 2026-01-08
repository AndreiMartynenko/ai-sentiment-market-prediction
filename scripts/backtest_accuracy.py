#!/usr/bin/env python3

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import requests

# Allow running as a script from repo root without installing as a package.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from ml_service.hybrid_engine import HybridEngine
from ml_service.indicators import TechnicalIndicators


@dataclass(frozen=True)
class EvalConfig:
    interval: str
    warmup_bars: int
    horizon_bars: int
    threshold: float


BINANCE_BASE_URL = "https://api.binance.com/api/v3"


def _to_ms(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_klines_full(
    symbol: str,
    interval: str,
    start: datetime,
    end: datetime,
    limit: int = 1000,
) -> pd.DataFrame:
    """Fetch full OHLCV history from Binance klines API using pagination."""
    url = f"{BINANCE_BASE_URL}/klines"

    start_ms = _to_ms(start)
    end_ms = _to_ms(end)

    all_rows: List[list] = []
    cur_start = start_ms

    while True:
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "startTime": cur_start,
            "endTime": end_ms,
            "limit": min(limit, 1000),
        }
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        rows = resp.json() or []
        if not rows:
            break

        all_rows.extend(rows)

        last_open_time = int(rows[-1][0])
        next_start = last_open_time + 1
        if next_start <= cur_start:
            break
        cur_start = next_start

        if last_open_time >= end_ms:
            break

        # If Binance returns fewer than limit rows, we've reached the end.
        if len(rows) < params["limit"]:
            break

    if not all_rows:
        raise RuntimeError(f"No klines returned for {symbol} {interval} in range")

    df = pd.DataFrame(
        all_rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "num_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.set_index("timestamp")

    out = df[["open", "high", "low", "close", "volume"]].copy()
    out = out.dropna()
    return out


def label_from_forward_return(r: float, threshold: float) -> str:
    if r >= threshold:
        return "BUY"
    if r <= -threshold:
        return "SELL"
    return "HOLD"


def compute_metrics(rows: List[Dict]) -> Dict[str, float]:
    if not rows:
        return {}

    labels = ["BUY", "SELL", "HOLD"]
    conf: Dict[Tuple[str, str], int] = {(p, t): 0 for p in labels for t in labels}

    for r in rows:
        conf[(r["pred_signal"], r["true_label"])] += 1

    total = len(rows)
    correct = sum(conf[(x, x)] for x in labels)
    accuracy = correct / total if total else 0.0

    def prf(target: str) -> Tuple[float, float, float]:
        tp = conf[(target, target)]
        fp = sum(conf[(target, t)] for t in labels if t != target)
        fn = sum(conf[(p, target)] for p in labels if p != target)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        return precision, recall, f1

    buy_p, buy_r, buy_f1 = prf("BUY")
    sell_p, sell_r, sell_f1 = prf("SELL")

    pred_buy_sell = sum(1 for r in rows if r["pred_signal"] in {"BUY", "SELL"})
    coverage = pred_buy_sell / total if total else 0.0

    return {
        "n": float(total),
        "accuracy": accuracy,
        "buy_precision": buy_p,
        "buy_recall": buy_r,
        "buy_f1": buy_f1,
        "sell_precision": sell_p,
        "sell_recall": sell_r,
        "sell_f1": sell_f1,
        "coverage_buy_sell": coverage,
    }


def backtest_symbol(
    symbol: str,
    df: pd.DataFrame,
    cfg: EvalConfig,
    indicators: TechnicalIndicators,
    engine: HybridEngine,
) -> Tuple[List[Dict], Dict[str, float]]:
    rows: List[Dict] = []

    closes = df["close"].to_numpy(dtype=float)

    for i in range(cfg.warmup_bars, len(df) - cfg.horizon_bars):
        hist = df.iloc[: i + 1]

        ema20_s = indicators.calculate_ema(hist, period=20)
        ema50_s = indicators.calculate_ema(hist, period=50)
        rsi_s = indicators.calculate_rsi(hist, period=14)
        macd_d = indicators.calculate_macd(hist, fast=12, slow=26, signal=9)

        ema20 = float(ema20_s.iloc[-1]) if len(ema20_s) else np.nan
        ema50 = float(ema50_s.iloc[-1]) if len(ema50_s) else np.nan
        rsi = float(rsi_s.iloc[-1]) if len(rsi_s) else np.nan

        macd_line_s = macd_d.get("macd")
        macd_sig_s = macd_d.get("signal")
        macd_line = float(macd_line_s.iloc[-1]) if macd_line_s is not None and len(macd_line_s) else np.nan
        macd_sig = float(macd_sig_s.iloc[-1]) if macd_sig_s is not None and len(macd_sig_s) else None

        technical_score = indicators.calculate_technical_score(
            ema20=ema20,
            ema50=ema50,
            rsi=rsi,
            macd_line=macd_line,
            macd_signal=macd_sig,
        )

        # Current implementation treats sentiment/volatility as optional; we fix to 0 here for repeatability.
        sentiment_score = 0.0
        volatility_index = 0.0

        hybrid_score = engine.compute_hybrid_score(sentiment_score, technical_score, volatility_index)
        pred_signal, reason = engine.generate_signal(hybrid_score)
        confidence = engine.compute_confidence(sentiment_score, technical_score, volatility_index)

        # Forward return label
        c0 = closes[i]
        c1 = closes[i + cfg.horizon_bars]
        r = (c1 - c0) / c0 if c0 else 0.0
        true_label = label_from_forward_return(r, cfg.threshold)

        ts = df.index[i]

        rows.append(
            {
                "symbol": symbol,
                "timestamp": ts.isoformat(),
                "close": float(c0),
                "future_close": float(c1),
                "forward_return": float(r),
                "true_label": true_label,
                "pred_signal": pred_signal,
                "hybrid_score": float(hybrid_score),
                "technical_score": float(technical_score),
                "sentiment_score": float(sentiment_score),
                "volatility_index": float(volatility_index),
                "confidence": float(confidence),
                "reason": reason,
            }
        )

    metrics = compute_metrics(rows)
    return rows, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline accuracy backtest for ProofOfSignal")
    parser.add_argument(
        "--symbols",
        default="BTCUSDT,ETHUSDT",
        help="Comma-separated Binance symbols (default: BTCUSDT,ETHUSDT)",
    )
    parser.add_argument("--interval", default="1h", help="Binance kline interval (default: 1h)")
    parser.add_argument("--start", default="2025-10-01", help="UTC start date YYYY-MM-DD")
    parser.add_argument("--end", default="2026-01-31", help="UTC end date YYYY-MM-DD")
    parser.add_argument("--threshold", type=float, default=0.02, help="Return threshold θ (default: 0.02 = 2%%)")
    parser.add_argument("--horizon", type=int, default=24, help="Horizon in bars H (default: 24 bars)")
    parser.add_argument("--warmup", type=int, default=80, help="Warm-up bars before scoring (default: 80)")
    parser.add_argument("--out", default="backtest_results.csv", help="Output CSV filename")

    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)

    cfg = EvalConfig(
        interval=args.interval,
        warmup_bars=int(args.warmup),
        horizon_bars=int(args.horizon),
        threshold=float(args.threshold),
    )

    indicators = TechnicalIndicators()
    # Evaluation mode: technical-driven scoring.
    # Rationale: the production API currently uses neutral sentiment/volatility defaults in no-DB mode,
    # which can suppress BUY/SELL coverage. For accuracy evaluation on historical candles we therefore
    # evaluate the technical component as the primary decision driver.
    engine = HybridEngine(sentiment_weight=0.0, technical_weight=1.0, volatility_weight=0.0)

    all_rows: List[Dict] = []
    summary: Dict[str, Dict[str, float]] = {}

    for sym in symbols:
        df = fetch_klines_full(sym, cfg.interval, start, end)
        rows, metrics = backtest_symbol(sym, df, cfg, indicators, engine)
        all_rows.extend(rows)
        summary[sym] = metrics

    out_df = pd.DataFrame(all_rows)
    out_df.to_csv(args.out, index=False)

    # Print a copy-paste friendly summary
    print("\nBacktest Summary")
    print(f"Range (UTC): {args.start} → {args.end}")
    print(f"Interval: {cfg.interval}, Horizon: {cfg.horizon_bars} bars, Threshold θ: {cfg.threshold:.2%}")
    print("")

    def fmt(x: float) -> str:
        return f"{x:.3f}" if isinstance(x, (float, int)) else str(x)

    print("Symbol, N, Accuracy, BUY P/R/F1, SELL P/R/F1, Coverage(BUY+SELL)")
    for sym, m in summary.items():
        if not m:
            continue
        print(
            ", ".join(
                [
                    sym,
                    str(int(m["n"])),
                    fmt(m["accuracy"]),
                    f"{fmt(m['buy_precision'])}/{fmt(m['buy_recall'])}/{fmt(m['buy_f1'])}",
                    f"{fmt(m['sell_precision'])}/{fmt(m['sell_recall'])}/{fmt(m['sell_f1'])}",
                    fmt(m["coverage_buy_sell"]),
                ]
            )
        )

    print(f"\nSaved CSV: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
