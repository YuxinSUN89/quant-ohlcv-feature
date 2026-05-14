import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    eps = config.eps
    # FiRsi indicator
    # Formula: FI = VOLUME * (CLOSE - REF(CLOSE, 1)); RSI applied to FI series
    # Force Index (FI) combines price change and volume. RSI is then computed on FI to measure
    # whether buying or selling force is gaining momentum. EMA smoothing is applied at the end.
    # A value above 0.5 suggests increasing buying force; below 0.5 suggests selling force.
    df = df.with_columns(pl.Series("_fi", df["volume"] * (df["close"] - df["close"].shift(1))))

    diff = df["_fi"].diff()
    df = df.with_columns(pl.Series("up", np.where(diff > 0, diff, 0)).fill_nan(None))
    df = df.with_columns(pl.Series("down", np.where(diff < 0, abs(diff), 0)).fill_nan(None))
    A = df["up"].rolling_sum(n, min_samples=config.min_periods)
    B = df["down"].rolling_sum(n, min_samples=config.min_periods)
    RSI = A / (A + B + eps)

    s = RSI.ewm_mean(span=n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series(factor_name, s))

    return df
