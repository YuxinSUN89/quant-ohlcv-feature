import numpy as np
import pandas as pd


def signal(df, n, factor_name, config):
    eps = config.eps
    # FiRsi indicator
    # Formula: FI = VOLUME * (CLOSE - REF(CLOSE, 1)); RSI applied to FI series
    # Force Index (FI) combines price change and volume. RSI is then computed on FI to measure
    # whether buying or selling force is gaining momentum. EMA smoothing is applied at the end.
    # A value above 0.5 suggests increasing buying force; below 0.5 suggests selling force.
    df["_fi"] = df["volume"] * (df["close"] - df["close"].shift(1))

    diff = df["_fi"].diff()
    df["up"] = np.where(diff > 0, diff, 0)
    df["down"] = np.where(diff < 0, abs(diff), 0)
    A = df["up"].rolling(n, min_periods=config.min_periods).sum()
    B = df["down"].rolling(n, min_periods=config.min_periods).sum()
    RSI = A / (A + B + eps)

    s = RSI.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    df[factor_name] = pd.Series(s)

    return df
