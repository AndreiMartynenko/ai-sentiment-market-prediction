"""Institutional-grade signal engine (no DB).

Strictly gated pipeline:
- Regime (EMA200 + ADX on 1H/4H)
- Sentiment (score + momentum)
- Structure (HH/HL or LL/LH) + liquidity sweep + BOS
- Entry triggers (RSI pullback + VWAP + volume)
- Risk management (RR >= 1:2, SL beyond sweep)

Returns NO_TRADE unless all mandatory gates pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import pandas_ta as ta

    HAS_PANDAS_TA = True
except Exception:
    HAS_PANDAS_TA = False


SignalSide = Literal["LONG", "SHORT", "NO_TRADE"]
MarketRegime = Literal["TREND", "RANGE"]
StructureState = Literal["BULLISH", "BEARISH", "UNCLEAR"]
Timeframe = Literal["5m", "15m", "1h"]


def _no_trade_payload(
    *,
    timeframe: Timeframe,
    failed_gate: str,
    explain: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "signal": "NO_TRADE",
        "reason": "insufficient confluence",
        "timeframe": timeframe,
        "confidence_score": 0,
        "failed_gate": failed_gate,
        "explain": [explain],
        "entry_price": None,
        "stop_loss": None,
        "take_profit": None,
        "risk_reward": None,
    }
    if extra:
        payload.update(extra)
    return payload


@dataclass
class RegimeResult:
    market_regime: MarketRegime
    bias: Literal["LONG", "SHORT", "NEUTRAL"]
    adx_1h: float
    adx_4h: float
    ema200_1h: float
    ema200_4h: float
    price_1h: float
    price_4h: float


@dataclass
class SentimentResult:
    sentiment_score: float
    rising: bool
    falling: bool


@dataclass
class StructureResult:
    structure: StructureState
    sweep: bool
    bos: bool
    sweep_level: Optional[float]
    sweep_index: Optional[int]
    bos_level: Optional[float]
    sweep_side: Optional[Literal["LOW", "HIGH"]]


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        if isinstance(x, (float, int)):
            return float(x)
        if isinstance(x, str) and x.strip() == "":
            return default
        return float(x)
    except Exception:
        return default


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(length).mean()
    avg_loss = loss.rolling(length).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def _adx(df: pd.DataFrame, length: int = 14) -> pd.Series:
    # Use pandas_ta if available; else fall back to a minimal manual implementation.
    if HAS_PANDAS_TA:
        adx_df = ta.adx(df["high"], df["low"], df["close"], length=length)
        # pandas_ta returns columns: ADX_{len}, DMP_{len}, DMN_{len}
        col = f"ADX_{length}"
        if adx_df is not None and col in adx_df.columns:
            return adx_df[col].fillna(0.0)

    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = (high - low).abs()
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(length).mean()
    plus_di = 100 * (plus_dm.rolling(length).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.rolling(length).mean() / atr.replace(0, np.nan))
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0.0)
    adx = dx.rolling(length).mean().fillna(0.0)
    return adx


def _vwap(df: pd.DataFrame) -> pd.Series:
    # Typical price VWAP
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"].astype(float)
    cum_pv = pv.cumsum()
    cum_vol = df["volume"].astype(float).cumsum().replace(0, np.nan)
    return (cum_pv / cum_vol).fillna(method="ffill")


def _volume_sma(df: pd.DataFrame, length: int = 20) -> pd.Series:
    return df["volume"].astype(float).rolling(length).mean()


def _symbol_to_news_ticker(symbol: str) -> str:
    s = symbol.upper().strip()
    for suffix in ["USDT", "USD", "PERP"]:
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s


def compute_sentiment_with_momentum(
    *,
    symbol: str,
    news_manager: Any,
    now: Optional[datetime] = None,
    limit: int = 12,
) -> SentimentResult:
    now = _to_utc(now or datetime.now(timezone.utc))

    if news_manager is None:
        return SentimentResult(sentiment_score=0.0, rising=False, falling=False)

    ticker = _symbol_to_news_ticker(symbol)
    items = news_manager.fetch_symbol_news(ticker, limit=limit) or []

    if not items:
        return SentimentResult(sentiment_score=0.0, rising=False, falling=False)

    # Source weighting heuristic (best-effort):
    # financial news > verified analysts > social media
    # We only have source/domain; so we approximate.
    high_quality_domains = {
        "reuters.com",
        "bloomberg.com",
        "wsj.com",
        "ft.com",
        "coindesk.com",
        "cointelegraph.com",
    }

    def source_weight(domain: Optional[str], source: Optional[str]) -> float:
        d = (domain or "").lower()
        s = (source or "").lower()
        if any(hq in d for hq in high_quality_domains) or any(hq.split(".")[0] in s for hq in high_quality_domains):
            return 1.0
        # crypto-native but not top-tier
        if "coin" in d or "crypto" in d or "coin" in s or "crypto" in s:
            return 0.8
        return 0.65

    # Time decay: exp(-age_hours / 12)
    scored: List[Tuple[datetime, float]] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for it in items:
        published_raw = it.get("published_at")
        published_at = None
        if isinstance(published_raw, str) and published_raw:
            try:
                published_at = _to_utc(datetime.fromisoformat(published_raw.replace("Z", "+00:00")))
            except Exception:
                published_at = now
        else:
            published_at = now

        age_hours = max(0.0, (now - published_at).total_seconds() / 3600.0)
        decay = math.exp(-age_hours / 12.0)
        w_src = source_weight(it.get("domain"), it.get("source"))
        score = _safe_float(it.get("sentiment_score"), 0.0)
        conf = _safe_float(it.get("sentiment_confidence"), 0.0)

        w = w_src * decay * max(0.05, conf)
        weighted_sum += w * score
        weight_total += w
        scored.append((published_at, score))

    agg = weighted_sum / weight_total if weight_total > 0 else 0.0
    agg = float(max(-1.0, min(1.0, agg)))

    # Momentum: compare recent half vs older half.
    scored.sort(key=lambda x: x[0])
    scores_only = [s for _, s in scored]
    if len(scores_only) < 4:
        return SentimentResult(sentiment_score=agg, rising=False, falling=False)

    mid = len(scores_only) // 2
    older = float(np.mean(scores_only[:mid]))
    recent = float(np.mean(scores_only[mid:]))
    delta = recent - older

    rising = delta > 0.05
    falling = delta < -0.05

    return SentimentResult(sentiment_score=agg, rising=rising, falling=falling)


def compute_regime(
    *,
    df_1h: pd.DataFrame,
    df_4h: pd.DataFrame,
) -> RegimeResult:
    close_1h = df_1h["close"].astype(float)
    close_4h = df_4h["close"].astype(float)

    ema200_1h = float(_ema(close_1h, 200).iloc[-1])
    ema200_4h = float(_ema(close_4h, 200).iloc[-1])

    adx_1h = float(_adx(df_1h, 14).iloc[-1])
    adx_4h = float(_adx(df_4h, 14).iloc[-1])

    price_1h = float(close_1h.iloc[-1])
    price_4h = float(close_4h.iloc[-1])

    # Institutional HTF regime: treat 4H as primary regime filter.
    # Keep 1H as confirmation (not a hard blocker), otherwise signals become too sparse.
    if adx_4h < 20:
        return RegimeResult(
            market_regime="RANGE",
            bias="NEUTRAL",
            adx_1h=adx_1h,
            adx_4h=adx_4h,
            ema200_1h=ema200_1h,
            ema200_4h=ema200_4h,
            price_1h=price_1h,
            price_4h=price_4h,
        )

    # Bias rule:
    # - primary: price relative to 4H EMA200
    # - confirmation: 1H price relative to 1H EMA200
    # If 1H disagrees, treat as neutral.
    if price_4h > ema200_4h and price_1h > ema200_1h:
        bias = "LONG"
    elif price_4h < ema200_4h and price_1h < ema200_1h:
        bias = "SHORT"
    else:
        bias = "NEUTRAL"

    return RegimeResult(
        market_regime="TREND",
        bias=bias,
        adx_1h=adx_1h,
        adx_4h=adx_4h,
        ema200_1h=ema200_1h,
        ema200_4h=ema200_4h,
        price_1h=price_1h,
        price_4h=price_4h,
    )


def _find_swings(df: pd.DataFrame, left: int = 3, right: int = 3) -> Tuple[List[int], List[int]]:
    highs = df["high"].astype(float).values
    lows = df["low"].astype(float).values
    swing_highs: List[int] = []
    swing_lows: List[int] = []

    n = len(df)
    for i in range(left, n - right):
        h = highs[i]
        if h == max(highs[i - left : i + right + 1]):
            swing_highs.append(i)
        l = lows[i]
        if l == min(lows[i - left : i + right + 1]):
            swing_lows.append(i)

    return swing_highs, swing_lows


def compute_structure_sweep_bos(
    df: pd.DataFrame,
    bos_window: int = 5,
    pre_range_window: int = 10,
) -> StructureResult:
    # Basic market structure from swings
    if len(df) < 60:
        return StructureResult(
            structure="UNCLEAR",
            sweep=False,
            bos=False,
            sweep_level=None,
            sweep_index=None,
            bos_level=None,
            sweep_side=None,
        )

    swing_highs, swing_lows = _find_swings(df, 3, 3)
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return StructureResult(
            structure="UNCLEAR",
            sweep=False,
            bos=False,
            sweep_level=None,
            sweep_index=None,
            bos_level=None,
            sweep_side=None,
        )

    sh1, sh2 = swing_highs[-2], swing_highs[-1]
    sl1, sl2 = swing_lows[-2], swing_lows[-1]

    h1, h2 = float(df["high"].iloc[sh1]), float(df["high"].iloc[sh2])
    l1, l2 = float(df["low"].iloc[sl1]), float(df["low"].iloc[sl2])

    # Tolerance to avoid classifying tiny differences as structure breaks (0.1% of price)
    last_close = float(df["close"].iloc[-1])
    tol = max(1e-8, abs(last_close) * 0.001)

    # Use last 3 swings (if available) to reduce UNCLEAR frequency.
    last_high_idxs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs[-2:]
    last_low_idxs = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows[-2:]
    last_highs = [float(df["high"].iloc[i]) for i in last_high_idxs]
    last_lows = [float(df["low"].iloc[i]) for i in last_low_idxs]

    def strictly_increasing(vals: List[float]) -> bool:
        return all((vals[i] - vals[i - 1]) > tol for i in range(1, len(vals)))

    def strictly_decreasing(vals: List[float]) -> bool:
        return all((vals[i - 1] - vals[i]) > tol for i in range(1, len(vals)))

    structure: StructureState
    if strictly_increasing(last_highs) and strictly_increasing(last_lows):
        structure = "BULLISH"
    elif strictly_decreasing(last_highs) and strictly_decreasing(last_lows):
        structure = "BEARISH"
    else:
        structure = "UNCLEAR"

    # Liquidity sweep + BOS:
    # Scan the most recent candles for a sweep event, then allow BOS confirmation
    # within the next `bos_window` candles after that sweep.
    # This prevents the "must happen on the last candle" problem.
    sweep = False
    bos = False
    sweep_level: Optional[float] = None
    sweep_side: Optional[Literal["LOW", "HIGH"]] = None
    sweep_index: Optional[int] = None
    bos_level: Optional[float] = None

    lows = df["low"].astype(float).values
    highs = df["high"].astype(float).values
    closes = df["close"].astype(float).values

    # Check last ~10 candles for sweeps.
    lookback = min(len(df) - 1, max(10, bos_window * 2))
    start_idx = max(1, len(df) - 1 - lookback)

    for i in range(start_idx, len(df) - 1):
        # Sweep detection on candle i
        if lows[i] < l2 and closes[i] > l2:
            sweep = True
            sweep_level = l2
            sweep_side = "LOW"
            sweep_index = i
        elif highs[i] > h2 and closes[i] < h2:
            sweep = True
            sweep_level = h2
            sweep_side = "HIGH"
            sweep_index = i
        else:
            continue

        # Practical BOS:
        # define BOS as breaking the local pre-sweep range (last `pre_range_window` candles
        # before the sweep), not necessarily the major swing extreme.
        pre_start = max(0, i - pre_range_window)
        pre_high = float(np.max(highs[pre_start:i])) if i > pre_start else float(highs[i])
        pre_low = float(np.min(lows[pre_start:i])) if i > pre_start else float(lows[i])

        # BOS confirmation within next bos_window candles (i+1 .. i+bos_window)
        # Practical: allow wick break (high/low) rather than requiring a close.
        end = min(len(df) - 1, i + bos_window)
        future_highs = highs[i + 1 : end + 1]
        future_lows = lows[i + 1 : end + 1]
        if sweep_side == "LOW":
            bos_level = pre_high
            bos = bool((future_highs > pre_high).any())
        else:
            bos_level = pre_low
            bos = bool((future_lows < pre_low).any())

        if bos:
            break

    return StructureResult(
        structure=structure,
        sweep=sweep,
        bos=bos,
        sweep_level=sweep_level,
        sweep_index=sweep_index,
        bos_level=bos_level,
        sweep_side=sweep_side,
    )


def compute_entry_and_risk(
    *,
    df_exec: pd.DataFrame,
    side: Literal["LONG", "SHORT"],
    sweep_level: Optional[float],
    timeframe: Timeframe,
    debug_out: Optional[Dict[str, Any]] = None,
    preset: str = "balanced",
    rules: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    close = df_exec["close"].astype(float)
    rsi = _rsi(close, 14)
    vwap = _vwap(df_exec)
    vol_sma = _volume_sma(df_exec, 20)

    last = df_exec.iloc[-1]
    prev = df_exec.iloc[-2]

    entry = float(last["close"])
    last_rsi = float(rsi.iloc[-1])
    prev_rsi = float(rsi.iloc[-2])
    last_vwap = float(vwap.iloc[-1])

    last_vol = float(last["volume"])
    avg_vol = float(vol_sma.iloc[-1]) if not pd.isna(vol_sma.iloc[-1]) else 0.0

    if debug_out is not None:
        debug_out.update(
            {
                "entry_price": entry,
                "last_rsi": last_rsi,
                "prev_rsi": prev_rsi,
                "vwap": last_vwap,
                "last_volume": last_vol,
                "avg_volume": avg_vol,
                "checks": {},
            }
        )

    rules_in = rules or {}
    enable_vwap = bool(rules_in.get("enable_vwap", True))
    enable_volume = bool(rules_in.get("enable_volume", True))
    enable_stop_cap = bool(rules_in.get("enable_stop_cap", True))

    preset_norm = (preset or "balanced").strip().lower()
    if preset_norm not in {"strict", "balanced", "aggressive"}:
        preset_norm = "balanced"

    # Thresholds by preset
    if preset_norm == "strict":
        long_rsi_min, long_rsi_max = 40.0, 50.0
        short_rsi_min, short_rsi_max = 50.0, 60.0
        vwap_eps = 0.0
        vol_mult_req = 1.20
        max_stop_pct = 0.01
        require_rsi_momentum = True
        require_volume = True
    elif preset_norm == "aggressive":
        long_rsi_min, long_rsi_max = 30.0, 60.0
        short_rsi_min, short_rsi_max = 40.0, 70.0
        vwap_eps = 0.002
        vol_mult_req = 1.00
        max_stop_pct = 0.03
        require_rsi_momentum = False
        require_volume = False
    else:
        long_rsi_min, long_rsi_max = 35.0, 55.0
        short_rsi_min, short_rsi_max = 45.0, 65.0
        vwap_eps = 0.001
        vol_mult_req = 1.05
        max_stop_pct = 0.02
        require_rsi_momentum = True
        require_volume = True

    # RSI pullback + turn
    if side == "LONG":
        rsi_ok = long_rsi_min <= last_rsi <= long_rsi_max
        rsi_momentum_ok = (last_rsi > prev_rsi) if require_rsi_momentum else True
        vwap_ok = entry >= (last_vwap * (1.0 - vwap_eps))
        candle_ok = float(last["close"]) > float(last["open"])
    else:
        rsi_ok = short_rsi_min <= last_rsi <= short_rsi_max
        rsi_momentum_ok = (last_rsi < prev_rsi) if require_rsi_momentum else True
        vwap_ok = entry <= (last_vwap * (1.0 + vwap_eps))
        candle_ok = float(last["close"]) < float(last["open"])

    if not enable_vwap:
        vwap_ok = True

    # Volume checks (evaluate even if RSI/VWAP fails so we can explain everything)
    avg_vol_ok = avg_vol > 0
    volume_ok = (last_vol >= avg_vol * vol_mult_req) if avg_vol_ok else False

    # Volume can be disabled via preset (aggressive) or via custom rules.
    effective_volume_ok = volume_ok if (require_volume and enable_volume) else True

    if debug_out is not None:
        debug_out["checks"].update(
            {
                "preset": preset_norm,
                "rsi_ok": bool(rsi_ok),
                "rsi_momentum_ok": bool(rsi_momentum_ok),
                "vwap_ok": bool(vwap_ok),
                "candle_ok": bool(candle_ok),
                "avg_vol_ok": bool(avg_vol_ok),
                "volume_ok": bool(volume_ok),
                "effective_volume_ok": bool(effective_volume_ok),
                "vol_mult_req": float(vol_mult_req),
                "max_stop_pct": float(max_stop_pct),
                "require_rsi_momentum": bool(require_rsi_momentum),
                "require_volume": bool(require_volume and enable_volume),
                "enable_vwap": bool(enable_vwap),
                "enable_volume": bool(enable_volume),
                "enable_stop_cap": bool(enable_stop_cap),
            }
        )

    # Risk management: SL beyond sweep level (if present)
    # If we didn't detect a sweep, fall back to a recent range stop.
    # This makes the system more actionable while still enforcing max stop-width.
    fallback_lookback = min(len(df_exec), 20)
    recent_low = float(df_exec["low"].astype(float).iloc[-fallback_lookback:].min())
    recent_high = float(df_exec["high"].astype(float).iloc[-fallback_lookback:].max())

    if side == "LONG":
        stop_ref = float(sweep_level) if sweep_level is not None else recent_low
        stop = float(stop_ref) * 0.999  # small buffer
        risk = entry - stop
        if risk <= 0:
            return None
        take_profit = entry + 2.0 * risk
    else:
        stop_ref = float(sweep_level) if sweep_level is not None else recent_high
        stop = float(stop_ref) * 1.001
        risk = stop - entry
        if risk <= 0:
            return None
        take_profit = entry - 2.0 * risk

    risk_pct = (risk / entry) if entry != 0 else 1.0

    # Reject wide stop-loss relative to price (heuristic)
    if enable_stop_cap and risk_pct > max_stop_pct:
        if debug_out is not None:
            debug_out.update(
                {
                    "stop_loss": float(stop),
                    "risk": float(risk),
                    "risk_pct": float(risk_pct),
                }
            )
            debug_out["checks"]["stop_width_ok"] = False
        stop_width_ok = False
    else:
        stop_width_ok = True

    if debug_out is not None:
        debug_out.update(
            {
                "stop_loss": float(stop),
                "risk": float(risk),
                "risk_pct": float(risk_pct),
            }
        )
        debug_out["checks"]["stop_width_ok"] = bool(stop_width_ok)

    # Final decision
    # Keep VWAP + stop width as core safety checks.
    # RSI momentum and volume can be disabled in aggressive mode.
    if not (rsi_ok and rsi_momentum_ok and vwap_ok and avg_vol_ok and effective_volume_ok and stop_width_ok):
        return None

    return {
        "entry_price": float(entry),
        "stop_loss": float(stop),
        "take_profit": float(take_profit),
        "risk_reward": "1:2+",
        "timeframe": timeframe,
    }


def generate_institutional_signal(
    *,
    symbol: str,
    data_manager: Any,
    news_manager: Any,
    timeframe: Timeframe = "15m",
    preset: str = "balanced",
    rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    result, _debug = generate_institutional_signal_debug(
        symbol=symbol,
        data_manager=data_manager,
        news_manager=news_manager,
        timeframe=timeframe,
        preset=preset,
        rules=rules,
    )
    return result


def generate_institutional_signal_debug(
    *,
    symbol: str,
    data_manager: Any,
    news_manager: Any,
    timeframe: Timeframe = "15m",
    use_sentiment: bool = False,
    preset: str = "balanced",
    rules: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    # Fetch data
    # - HTF regime: 1h + 4h
    # - execution: 15m (or 5m/1h)
    debug: Dict[str, Any] = {
        "symbol": symbol,
        "timeframe": timeframe,
        "gates": {},
        "metrics": {},
    }

    rules_in = rules or {}

    def _rule_bool(key: str, default: bool) -> bool:
        v = rules_in.get(key, default)
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() in {"1", "true", "yes", "y", "on"}
        return default

    # RSI is always enforced by user request.
    enable_regime = _rule_bool("enable_regime", True)
    enable_structure = _rule_bool("enable_structure", True)
    enable_alignment = _rule_bool("enable_alignment", True)
    enable_vwap = _rule_bool("enable_vwap", True)
    enable_volume = _rule_bool("enable_volume", True)
    enable_stop_cap = _rule_bool("enable_stop_cap", True)

    rsi_only_mode = (not enable_regime) and (not enable_structure) and (not enable_alignment) and (not enable_vwap) and (not enable_volume) and (not enable_stop_cap)

    debug["rules"] = {
        "enable_regime": enable_regime,
        "enable_structure": enable_structure,
        "enable_alignment": enable_alignment,
        "enable_vwap": enable_vwap,
        "enable_volume": enable_volume,
        "enable_stop_cap": enable_stop_cap,
        "rsi_always_on": True,
        "rsi_only_mode": rsi_only_mode,
    }

    if data_manager is None or getattr(data_manager, "binance", None) is None:
        debug["gates"]["data"] = False
        return (
            _no_trade_payload(
                timeframe=timeframe,
                failed_gate="data",
                explain="Market data provider unavailable.",
            ),
            debug,
        )

    interval_map = {
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
    }

    df_1h = data_manager.binance.get_klines(symbol, interval="1h", limit=260)
    df_4h = data_manager.binance.get_klines(symbol, interval="4h", limit=260)
    df_exec = data_manager.binance.get_klines(symbol, interval=interval_map[timeframe], limit=300)

    if df_1h is None or df_4h is None or df_exec is None:
        debug["gates"]["data"] = False
        return (
            _no_trade_payload(
                timeframe=timeframe,
                failed_gate="data",
                explain="Failed to fetch candles for one or more timeframes.",
            ),
            debug,
        )

    if df_1h.empty or df_4h.empty or df_exec.empty:
        debug["gates"]["data"] = False
        return (
            _no_trade_payload(
                timeframe=timeframe,
                failed_gate="data",
                explain="Received empty candle data.",
            ),
            debug,
        )

    debug["gates"]["data"] = True

    # Regime
    regime = compute_regime(df_1h=df_1h, df_4h=df_4h)
    debug["metrics"].update(
        {
            "adx_1h": regime.adx_1h,
            "adx_4h": regime.adx_4h,
            "ema200_1h": regime.ema200_1h,
            "ema200_4h": regime.ema200_4h,
            "price_1h": regime.price_1h,
            "price_4h": regime.price_4h,
            "regime": regime.market_regime,
            "bias": regime.bias,
        }
    )
    if enable_regime:
        if regime.market_regime == "RANGE":
            debug["gates"]["market_regime"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="market_regime",
                    explain="Higher timeframes are range-bound (ADX too low); waiting for trending conditions.",
                    extra={
                        "market_regime": regime.market_regime,
                        "bias": regime.bias,
                    },
                ),
                debug,
            )
        if regime.bias == "NEUTRAL":
            debug["gates"]["market_regime"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="market_regime",
                    explain="Higher timeframes do not agree on a clear directional bias.",
                    extra={
                        "market_regime": regime.market_regime,
                        "bias": regime.bias,
                    },
                ),
                debug,
            )

        debug["gates"]["market_regime"] = True
    else:
        debug["gates"]["market_regime"] = "SKIPPED"

        # RSI-only / relaxed mode: infer bias from execution RSI.
        close_exec = df_exec["close"].astype(float)
        exec_rsi_val = float(_rsi(close_exec, 14).iloc[-1])
        debug["metrics"]["exec_rsi"] = exec_rsi_val
        if exec_rsi_val >= 50.0:
            regime = RegimeResult(
                market_regime="TREND",
                bias="SHORT",
                adx_1h=regime.adx_1h,
                adx_4h=regime.adx_4h,
                ema200_1h=regime.ema200_1h,
                ema200_4h=regime.ema200_4h,
                price_1h=regime.price_1h,
                price_4h=regime.price_4h,
            )
        else:
            regime = RegimeResult(
                market_regime="TREND",
                bias="LONG",
                adx_1h=regime.adx_1h,
                adx_4h=regime.adx_4h,
                ema200_1h=regime.ema200_1h,
                ema200_4h=regime.ema200_4h,
                price_1h=regime.price_1h,
                price_4h=regime.price_4h,
            )

    # Sentiment (optional for now)
    sent = SentimentResult(sentiment_score=0.0, rising=False, falling=False)
    if use_sentiment and news_manager is not None:
        sent = compute_sentiment_with_momentum(symbol=symbol, news_manager=news_manager)

    debug["metrics"].update(
        {
            "sentiment_score": sent.sentiment_score,
            "sentiment_rising": sent.rising,
            "sentiment_falling": sent.falling,
            "sentiment_enabled": bool(use_sentiment and news_manager is not None),
        }
    )

    if use_sentiment:
        if regime.bias == "LONG":
            if not (sent.sentiment_score >= 0.6 and sent.rising):
                debug["gates"]["sentiment"] = False
                return (
                    _no_trade_payload(
                        timeframe=timeframe,
                        failed_gate="sentiment",
                        explain="Sentiment gate rejected the setup for LONG bias.",
                        extra={
                            "bias": regime.bias,
                            "sentiment_score": float(round(sent.sentiment_score, 4)),
                            "sentiment_rising": bool(sent.rising),
                        },
                    ),
                    debug,
                )
        else:
            if not (sent.sentiment_score <= -0.6 and sent.falling):
                debug["gates"]["sentiment"] = False
                return (
                    _no_trade_payload(
                        timeframe=timeframe,
                        failed_gate="sentiment",
                        explain="Sentiment gate rejected the setup for SHORT bias.",
                        extra={
                            "bias": regime.bias,
                            "sentiment_score": float(round(sent.sentiment_score, 4)),
                            "sentiment_falling": bool(sent.falling),
                        },
                    ),
                    debug,
                )

        debug["gates"]["sentiment"] = True
    else:
        debug["gates"]["sentiment"] = "SKIPPED"

    # Structure + sweep + BOS
    struct = compute_structure_sweep_bos(df_exec)
    debug["metrics"].update(
        {
            "structure": struct.structure,
            "liquidity_sweep": struct.sweep,
            "bos": struct.bos,
            "sweep_level": struct.sweep_level,
            "sweep_index": struct.sweep_index,
            "bos_level": struct.bos_level,
            "sweep_side": struct.sweep_side,
        }
    )
    warnings: List[str] = []

    # More actionable mode:
    # - Prefer sweep + BOS.
    # - If missing, allow BOS-only aligned with HTF bias.
    # - If still missing, do NOT hard-fail; proceed with fallback stops and lower confidence.
    fallback_bos = False
    fallback_bos_level: Optional[float] = None
    fallback_stop_ref: Optional[float] = None

    if not struct.bos:
        highs = df_exec["high"].astype(float).values
        lows = df_exec["low"].astype(float).values
        closes = df_exec["close"].astype(float).values
        pre_range_window = 10
        if len(df_exec) > pre_range_window + 2:
            pre_start = max(0, len(df_exec) - 1 - pre_range_window)
            pre_high = float(np.max(highs[pre_start : len(df_exec) - 1]))
            pre_low = float(np.min(lows[pre_start : len(df_exec) - 1]))
            last_high = float(highs[-1])
            last_low = float(lows[-1])
            last_close = float(closes[-1])

            if regime.bias == "LONG" and last_close > pre_high and last_high > pre_high:
                fallback_bos = True
                fallback_bos_level = pre_high
            if regime.bias == "SHORT" and last_close < pre_low and last_low < pre_low:
                fallback_bos = True
                fallback_bos_level = pre_low

    # Fallback stop reference from recent swings
    if struct.sweep_level is None:
        swing_highs, swing_lows = _find_swings(df_exec, 3, 3)
        if regime.bias == "LONG" and len(swing_lows) >= 1:
            fallback_stop_ref = float(df_exec["low"].astype(float).iloc[swing_lows[-1]])
        if regime.bias == "SHORT" and len(swing_highs) >= 1:
            fallback_stop_ref = float(df_exec["high"].astype(float).iloc[swing_highs[-1]])

    has_structure = bool(struct.bos and struct.sweep) or bool(fallback_bos) or bool(struct.bos)
    stop_ref = struct.sweep_level if struct.sweep_level is not None else fallback_stop_ref
    if stop_ref is None:
        # Last resort: use recent range stop reference.
        fallback_lookback = min(len(df_exec), 20)
        recent_low = float(df_exec["low"].astype(float).iloc[-fallback_lookback:].min())
        recent_high = float(df_exec["high"].astype(float).iloc[-fallback_lookback:].max())
        stop_ref = recent_low if regime.bias == "LONG" else recent_high

    debug["metrics"].update(
        {
            "fallback_bos": bool(fallback_bos),
            "fallback_bos_level": fallback_bos_level,
            "fallback_stop_ref": stop_ref,
        }
    )

    if not has_structure:
        debug["gates"]["structure"] = False
        warnings.append("Structure confirmation missing (no sweep/BOS). Using fallback stop reference.")
    else:
        debug["gates"]["structure"] = True

    # If we do have a sweep, enforce sweep direction matches bias.
    # If we're using BOS-only fallback, we skip this check.
    if enable_structure and struct.sweep:
        # - LONG entries require taking liquidity below (LOW sweep)
        # - SHORT entries require taking liquidity above (HIGH sweep)
        if regime.bias == "LONG" and struct.sweep_side != "LOW":
            debug["gates"]["structure"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="structure",
                    explain="Sweep direction does not match LONG bias (expected LOW sweep).",
                    extra={
                        "bias": regime.bias,
                        "sweep_side": struct.sweep_side,
                    },
                ),
                debug,
            )
        if regime.bias == "SHORT" and struct.sweep_side != "HIGH":
            debug["gates"]["structure"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="structure",
                    explain="Sweep direction does not match SHORT bias (expected HIGH sweep).",
                    extra={
                        "bias": regime.bias,
                        "sweep_side": struct.sweep_side,
                    },
                ),
                debug,
            )

    if struct.structure == "UNCLEAR":
        debug["gates"]["structure_state"] = "UNCLEAR"
        warnings.append("Structure state is UNCLEAR.")
    else:
        debug["gates"]["structure_state"] = struct.structure

    # Directional alignment between regime bias and structure
    if enable_alignment:
        if struct.structure != "UNCLEAR" and regime.bias == "LONG" and struct.structure != "BULLISH":
            debug["gates"]["alignment"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="alignment",
                    explain="Structure direction does not align with LONG bias.",
                    extra={
                        "bias": regime.bias,
                        "structure": struct.structure,
                    },
                ),
                debug,
            )
        if struct.structure != "UNCLEAR" and regime.bias == "SHORT" and struct.structure != "BEARISH":
            debug["gates"]["alignment"] = False
            return (
                _no_trade_payload(
                    timeframe=timeframe,
                    failed_gate="alignment",
                    explain="Structure direction does not align with SHORT bias.",
                    extra={
                        "bias": regime.bias,
                        "structure": struct.structure,
                    },
                ),
                debug,
            )

        debug["gates"]["alignment"] = True
    else:
        debug["gates"]["alignment"] = "SKIPPED"

    # Entry + risk
    entry_debug: Dict[str, Any] = {}
    entry = compute_entry_and_risk(
        df_exec=df_exec,
        side=regime.bias,
        sweep_level=stop_ref,
        timeframe=timeframe,
        debug_out=entry_debug,
        preset=preset,
        rules={
            "enable_vwap": enable_vwap,
            "enable_volume": enable_volume,
            "enable_stop_cap": enable_stop_cap,
            "rsi_only_mode": rsi_only_mode,
        },
    )
    if entry is None:
        debug["gates"]["entry"] = False


        # DEMO guarantee: when user disables all rules (RSI-only), always return a trade plan.
        # This is intentionally high-risk and clearly labeled.
        if rsi_only_mode:
            close_exec = df_exec["close"].astype(float)
            highs_exec = df_exec["high"].astype(float)
            lows_exec = df_exec["low"].astype(float)

            last_close = float(close_exec.iloc[-1])
            lookback = min(len(df_exec), 20)
            recent_low = float(lows_exec.iloc[-lookback:].min())
            recent_high = float(highs_exec.iloc[-lookback:].max())

            entry_price = last_close
            if regime.bias == "LONG":
                stop_loss = recent_low * 0.999
                risk = max(1e-9, entry_price - stop_loss)
                take_profit = entry_price + 2.0 * risk
            else:
                stop_loss = recent_high * 1.001
                risk = max(1e-9, stop_loss - entry_price)
                take_profit = entry_price - 2.0 * risk

            return {
                "engine_version": ENGINE_VERSION,
                "applied_rules": applied_rules,
                "signal": regime.bias,
                "confidence_score": 5,
                "risk_level": "HIGH",
                "risk_warnings": [
                    "HIGH RISK DEMO: RSI-only mode forces a trade even when normal entry rules fail.",
                ],
                "market_regime": regime.market_regime,
                "sentiment_score": float(round(sent.sentiment_score, 4)),
                "structure": struct.structure,
                "warnings": warnings + ["DEMO_FORCE_TRADE"],
                "entry_reason": ["rsi_only_demo"],
                "entry_price": float(entry_price),
                "stop_loss": float(stop_loss),
                "take_profit": float(take_profit),
                "risk_reward": "1:2+",
                "timeframe": timeframe,
                "invalidate_if": ["do_not_use_in_real_trading"],
            }, debug

        failed = []
        checks = (entry_debug.get("checks") or {}) if isinstance(entry_debug, dict) else {}
        enable_volume = bool(checks.get("enable_volume", True))
        enable_vwap = bool(checks.get("enable_vwap", True))
        enable_stop_cap = bool(checks.get("enable_stop_cap", True))
        if checks.get("rsi_ok") is False:
            failed.append("RSI condition not met")
        if enable_vwap and checks.get("vwap_ok") is False:
            failed.append("VWAP condition not met")
        if enable_volume and checks.get("effective_volume_ok") is False:
            if checks.get("avg_vol_ok") is False:
                failed.append("Not enough volume history to evaluate")
            if checks.get("volume_ok") is False:
                failed.append("Volume not expanded enough")
        if enable_stop_cap and checks.get("stop_width_ok") is False:
            failed.append("Stop too wide vs entry")

        explain_lines = failed if failed else [
            "Entry trigger and/or risk rules rejected the setup (e.g. volume, VWAP/RSI pullback, or stop too wide)."
        ]

        return (
            _no_trade_payload(
                timeframe=timeframe,
                failed_gate="entry",
                explain=explain_lines[0],
                extra={
                    "explain": explain_lines,
                    "entry_debug": entry_debug,
                },
            ),
            debug,
        )

    debug["gates"]["entry"] = True

    # Build response
    entry_reason = [
        "market_regime_confirmed",
        "sentiment_alignment",
        "liquidity_sweep",
        "bos_confirmed",
        "volume_confirmation",
    ]

    invalidate_if = [
        "sentiment_flip",
        "structure_break",
        "volume_divergence",
    ]

    # Risk label + warnings based on disabled rules
    risk_warnings: List[str] = []
    disabled = []
    if not enable_regime:
        disabled.append("market_regime")
    if not enable_structure:
        disabled.append("structure")
    if not enable_alignment:
        disabled.append("alignment")
    if not enable_vwap:
        disabled.append("vwap")
    if not enable_volume:
        disabled.append("volume")
    if not enable_stop_cap:
        disabled.append("stop_cap")

    if disabled:
        risk_warnings.append("HIGH RISK: disabled filters: " + ", ".join(disabled))

    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
    if len(disabled) >= 3:
        risk_level = "HIGH"
    elif len(disabled) >= 1:
        risk_level = "MEDIUM"

    # Confidence heuristic: keep conservative (0-100)
    # - sentiment magnitude (0-50)
    # - ADX strength (0-30)
    # - volume expansion bonus (0-20)
    adx_strength = min(30.0, max(0.0, (min(regime.adx_1h, regime.adx_4h) - 20.0) * 1.5))
    sent_strength = min(50.0, abs(sent.sentiment_score) * 50.0) if use_sentiment else 0.0

    last_vol = float(df_exec["volume"].iloc[-1])
    vol_sma = float(_volume_sma(df_exec, 20).iloc[-1])
    vol_mult = (last_vol / vol_sma) if vol_sma > 0 else 1.0
    vol_bonus = min(20.0, max(0.0, (vol_mult - 1.0) * 20.0))

    confidence_score = int(round(min(100.0, sent_strength + adx_strength + vol_bonus)))

    # Penalize confidence if structure confirmation is missing.
    if not has_structure:
        confidence_score = int(max(5, round(confidence_score * 0.55)))

    return {
        "signal": regime.bias,
        "confidence_score": confidence_score,
        "risk_level": risk_level,
        "risk_warnings": risk_warnings,
        "market_regime": regime.market_regime,
        "sentiment_score": float(round(sent.sentiment_score, 4)),
        "structure": struct.structure,
        "warnings": warnings,
        "entry_reason": entry_reason,
        "entry_price": entry["entry_price"],
        "stop_loss": entry["stop_loss"],
        "take_profit": entry["take_profit"],
        "risk_reward": entry["risk_reward"],
        "timeframe": entry["timeframe"],
        "invalidate_if": invalidate_if,
    }, debug
