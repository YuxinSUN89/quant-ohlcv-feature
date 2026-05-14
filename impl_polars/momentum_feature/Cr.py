import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Cr indicator (CR — Closing Rate vs Typical Price)
    # Formula: TYP = (HIGH+LOW+CLOSE)/3; H = MAX(HIGH - REF(TYP,1), 0); L = MAX(REF(TYP,1) - LOW, 0)
    #          CR = 100 * SUM(H, N) / SUM(L, N)
    # Measures how much the high exceeded yesterday's typical price versus how much the low fell below it.
    # CR > 100 suggests bullish pressure; CR < 100 suggests bearish pressure.
    _typ = (df["high"] + df["low"] + df["close"]) / 3
    _h = np.maximum(df["high"] - pl.Series(_typ).shift(1), 0)  # take the maximum of the two series
    _l = np.maximum(pl.Series(_typ).shift(1) - df["low"], 0)

    s = (
        100
        * pl.Series(_h).rolling_sum(n, min_samples=config.min_periods)
        / (config.normalize_eps + pl.Series(_l).rolling_sum(n, min_samples=config.min_periods))
    )
    df = df.with_columns(pl.Series(factor_name, s))

    return df
