"""
Strategy Sharing Session
Position Management Framework

Copyright reserved.

This code is for personal learning use only. Copying, modification, or commercial use without authorization is prohibited.
"""

import numpy as np


def signal(df, n, factor_name, config):
    df["avg_price"] = (df["close"] + df["high"] + df["low"]) / 3

    df["price_change"] = df["avg_price"].pct_change()
    df["amplitude"] = (df["high"] - df["low"]) / df["open"]
    # Numerical sensitivity note:
    # ZfAbsMean is unusually sensitive to tiny floating-point perturbations because the final
    # stage is a rolling percentile rank. Near-ties in amplitude_mean can flip the discrete
    # rank bucket (for example 1.0 -> 0.8333), so even tiny truncation differences can change
    # the output materially.
    df["amplitude"] = np.where(df["price_change"] > 0, df["amplitude"], 0)
    df["amplitude_mean"] = df["amplitude"].rolling(n, min_periods=config.min_periods).mean()

    df[factor_name] = df["amplitude_mean"].rolling(n, min_periods=config.min_periods).rank(ascending=True, pct=True)

    return df
