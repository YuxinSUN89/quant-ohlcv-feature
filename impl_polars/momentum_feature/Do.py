import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # DO indicator
    """
    DO=EMA(EMA(RSI,N),M)
    DO is the RSI indicator after smoothing (double moving average). DO greater than 0 indicates
    the market is in an uptrend, less than 0 indicates a downtrend. We use DO crossing above/below
    its moving average to generate buy/sell signals.
    """
    diff = df["close"].diff()
    df = df.with_columns(pl.Series("up", np.where(diff > 0, diff, 0)).fill_nan(None))
    df = df.with_columns(pl.Series("down", np.where(diff < 0, abs(diff), 0)).fill_nan(None))
    A = df["up"].rolling_sum(n, min_samples=config.min_periods)
    B = df["down"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("rsi", A / (A + B)))
    df = df.with_columns(pl.Series("ema_rsi", df["rsi"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, df["ema_rsi"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.drop("up")
    df = df.drop("down")
    df = df.drop("rsi")
    df = df.drop("ema_rsi")

    return df
