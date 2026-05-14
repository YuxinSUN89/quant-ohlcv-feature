import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Bias_v3 indicator (log-scale Bias normalized by 0.03)
    # Formula: MA = MA(CLOSE, N); result = log(CLOSE / (MA + eps)) / 0.03
    # Computes logarithmic deviation of close from its moving average, normalized by a fixed scale factor.
    # Positive values indicate close is above MA (upward bias); negative below.
    # Division by 0.03 normalizes the log-returns to a reasonable numeric range.
    eps = config.eps
    ma = df["close"].rolling_mean(n, min_samples=config.min_periods)
    # will output nan, / 0.03 to normalize data
    df = df.with_columns(pl.Series(factor_name, np.log((df["close"] / (ma + eps))) / 0.03))

    return df
