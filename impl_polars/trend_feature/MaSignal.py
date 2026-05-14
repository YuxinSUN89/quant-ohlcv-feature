import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # MaSignal indicator (Close - MA, 0-1 normalized)
    # Formula: result = scale_01(CLOSE - MA(CLOSE, N, config.normalize_eps), N)
    # Measures the deviation of close from its MA, normalized to [0,1].
    # Values above 0.5 indicate close is above the MA; below 0.5 indicates below the MA.
    s = df["close"] - df["close"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
