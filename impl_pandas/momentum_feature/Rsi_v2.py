import numpy as np


def signal(df, n, factor_name, config):
    # Rsi_v2 indicator (RSI using rolling sum instead of EWM)
    # Formula: A = SUM(MAX(DIFF,0), N); B = SUM(MAX(-DIFF,0), N)
    #          result = A / (A + B)
    # Standard RSI computed using rolling sum (Wilder-style but without EWM).
    # Range [0, 1]. Values above 0.7 indicate overbought; below 0.3 indicate oversold.
    eps = config.eps
    close_dif = df["close"].diff()
    df["up"] = np.where(close_dif > 0, close_dif, 0)
    df["down"] = np.where(close_dif < 0, abs(close_dif), 0)
    a = df["up"].rolling(n, min_periods=config.min_periods).sum()
    b = df["down"].rolling(n, min_periods=config.min_periods).sum()
    df[factor_name] = a / (a + b + eps)

    # remove redundant columns
    del df["up"], df["down"]

    return df
