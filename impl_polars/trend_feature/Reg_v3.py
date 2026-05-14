import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Reg_v3 indicator (Close vs OLS linear regression)
    # Formula: OLS fit of CLOSE over N time steps; REG = predicted value at last step (y = ax + b)
    #          result = CLOSE / (REG + eps) - 1
    # Uses closed-form OLS (no sklearn/polyfit) for numerically stable rolling regression.
    # Positive values indicate close is above the fitted trend; negative below.
    eps = config.eps

    # rolling OLS regression using numpy polyfit
    close_np = np.array(df["close"], dtype=float)
    reg_close = np.full(len(close_np), np.nan)
    min_periods = config.min_periods or 1
    for i in range(min_periods - 1, len(close_np)):
        start = max(0, i - n + 1)
        _y = close_np[start : i + 1]
        m = len(_y)
        if m < 2:
            reg_close[i] = _y[-1]
            continue
        x = np.arange(m, dtype=float)
        x_mean = (m - 1) / 2.0
        y_mean = _y.mean()
        slope = np.dot(x - x_mean, _y - y_mean) / (np.dot(x - x_mean, x - x_mean) + eps)
        intercept = y_mean - slope * x_mean
        reg_close[i] = slope * (m - 1) + intercept
    df = df.with_columns(pl.Series("reg_close", reg_close))
    df = df.with_columns(pl.Series(factor_name, (df["close"] / (df["reg_close"] + eps) - 1).fill_nan(None)))

    # remove redundant columns
    df = df.drop("reg_close")

    return df
