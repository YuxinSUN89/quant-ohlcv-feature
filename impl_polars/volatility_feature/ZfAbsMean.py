"""
Strategy Sharing Session
Position Management Framework

Copyright reserved.

This code is for personal learning use only. Copying, modification, or commercial use without authorization is prohibited.
"""

import numpy as np
import polars as pl


def rolling_rank_pct(s, n):
    """Compute rolling percentile rank using numpy, matching pandas rolling.rank(pct=True)."""
    a = s.to_numpy()
    result = np.full(len(a), np.nan)
    for i in range(len(a)):
        start = max(0, i - n + 1)
        window = a[start : i + 1]
        valid = window[~np.isnan(window)]
        if len(valid) < 1:
            continue
        last_val = valid[-1] if len(valid) > 0 else np.nan
        less = np.sum(valid < last_val)
        leq = np.sum(valid <= last_val)
        # pandas rank(method='average', pct=True): average rank of ties divided by len(valid)
        avg_rank = (less + 1 + leq) / 2
        result[i] = avg_rank / len(valid)
    return pl.Series(result)


def signal(df, n, factor_name, config):
    df = df.with_columns(pl.Series("avg_price", (df["close"] + df["high"] + df["low"]) / 3))

    df = df.with_columns(pl.Series("price_change", df["avg_price"].pct_change()))
    df = df.with_columns(pl.Series("amplitude", (df["high"] - df["low"]) / df["open"]))
    df = df.with_columns(pl.Series("amplitude", np.where(df["price_change"] > 0, df["amplitude"], 0)).fill_nan(0))
    # Numerical sensitivity note:
    # ZfAbsMean is unusually sensitive to tiny floating-point perturbations because the final
    # stage is a rolling percentile rank. Near-ties in amplitude_mean can flip the discrete
    # rank bucket (for example 1.0 -> 0.8333). We round here to reduce pandas/polars tie-noise;
    # any further changes should be parity-tested carefully.
    df = df.with_columns(
        pl.Series("amplitude_mean", df["amplitude"].rolling_mean(n, min_samples=config.min_periods).round(12))
    )

    df = df.with_columns(pl.Series(factor_name, rolling_rank_pct(df["amplitude_mean"], n)))

    return df
