import numpy as np


def signal(df, n, factor_name, config):
    # DO indicator
    """
    DO=EMA(EMA(RSI,N),M)
    DO is the RSI indicator after smoothing (double moving average). DO greater than 0 indicates
    the market is in an uptrend, less than 0 indicates a downtrend. We use DO crossing above/below
    its moving average to generate buy/sell signals.
    """
    diff = df["close"].diff()
    df["up"] = np.where(diff > 0, diff, 0)
    df["down"] = np.where(diff < 0, abs(diff), 0)
    A = df["up"].rolling(n, min_periods=config.min_periods).sum()
    B = df["down"].rolling(n, min_periods=config.min_periods).sum()
    df["rsi"] = A / (A + B)
    df["ema_rsi"] = df["rsi"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df[factor_name] = df["ema_rsi"].ewm(span=n, adjust=config.ewm_adjust).mean()

    del df["up"]
    del df["down"]
    del df["rsi"]
    del df["ema_rsi"]

    return df
