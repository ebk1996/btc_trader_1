import numpy as np
import pandas as pd
import yfinance as yf

def _extract_close(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with a single 'close' column regardless of whether df_in
    has flat columns (Close) or a MultiIndex with any ordering of levels.
    """
    df = df_in.copy()

    # Handle different yfinance shapes robustly
    if isinstance(df.columns, pd.MultiIndex):
        # Search every column tuple for a level named 'close' (case-insensitive)
        close_col = None
        for col in df.columns:
            names = [str(x).lower() for x in (col if isinstance(col, tuple) else (col,))]
            if "close" in names or "adj close" in names:
                close_col = col
                break
        if close_col is None:
            # As a fallback, try columns whose last level is Close-ish
            candidates = [c for c in df.columns if str(c[-1]).lower() in ("close", "adj close")]
            if candidates:
                close_col = candidates[0]
        if close_col is None:
            raise RuntimeError(f"Could not locate a 'Close' column in MultiIndex: {list(df.columns)[:6]} ...")
        close = df[close_col]
    else:
        # Flat columns; normalize names and pick close/adj close
        cols_map = {str(c).lower(): c for c in df.columns}
        if "close" in cols_map:
            close = df[cols_map["close"]]
        elif "adj close" in cols_map:
            close = df[cols_map["adj close"]]
        else:
            raise RuntimeError(f"'close' not found; got columns: {list(df.columns)}")

    # Ensure it is a 1-D Series with a clean name
    if isinstance(close, pd.DataFrame):
        # if it was a single-column DataFrame, collapse to Series
        if close.shape[1] == 1:
            close = close.iloc[:, 0]
        else:
            # pick first if multiple, but warn by raising for clarity
            raise RuntimeError(f"Ambiguous close columns found: {list(close.columns)}")
    close = close.astype("float64")
    out = pd.DataFrame({"close": close})
    out = out.dropna()
    return out

def fetch_history(yf_ticker: str, period="30d", interval="15m") -> pd.DataFrame:
    # Keep layout stable; explicit auto_adjust avoids the warning & surprises
    df_raw = yf.download(
        yf_ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="column"
    )
    if df_raw is None or len(df_raw) == 0:
        raise RuntimeError("No data from Yahoo Finance.")
    df = _extract_close(df_raw)
    if df.empty:
        raise RuntimeError("History contained no valid 'close' data.")
    return df

def signal_ma_cross(df: pd.DataFrame, fast: int, slow: int) -> str:
    df = df.copy()
    fast = int(fast); slow = int(slow)

    df["fast"] = df["close"].rolling(fast, min_periods=fast).mean()
    df["slow"] = df["close"].rolling(slow, min_periods=slow).mean()

    if len(df) < slow + 2:
        return "HOLD"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Convert to floats to avoid Series ambiguity
    try:
        pf, ps = float(prev["fast"]), float(prev["slow"])
        lf, ls = float(last["fast"]), float(last["slow"])
    except Exception:
        return "HOLD"

    vals = np.array([pf, ps, lf, ls], dtype=float)
    if not np.isfinite(vals).all():
        return "HOLD"

    if pf <= ps and lf > ls:
        return "BUY"
    if pf >= ps and lf < ls:
        return "SELL"
    return "HOLD"
