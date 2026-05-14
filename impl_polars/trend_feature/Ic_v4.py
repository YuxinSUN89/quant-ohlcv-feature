import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Ic_v4 indicator (IC close position within cloud, 0-1 normalized)
    # Formula: TS = (MAX(HIGH,N) + MIN(LOW,N))/2; KS = (MAX(HIGH,2N) + MIN(LOW,2N))/2
    #          SPAN_A = (TS + KS)/2; SPAN_B = (MAX(HIGH,3N) + MIN(LOW,3N))/2
    #          result = scale_01((CLOSE - SPAN_B, config.normalize_eps) / (SPAN_A - SPAN_B), N)
    # Measures where the close sits within the Ichimoku cloud, normalized to [0,1].
    # Same as Ic_v2 but with additional 0-1 normalization for comparability across periods.
    high_max1 = df["high"].rolling_max(n, min_samples=config.min_periods)
    high_max2 = df["high"].rolling_max(int(2 * n), min_samples=config.min_periods)
    high_max3 = df["high"].rolling_max(int(3 * n), min_samples=config.min_periods)
    low_min1 = df["low"].rolling_min(n, min_samples=config.min_periods)
    low_min2 = df["low"].rolling_min(int(2 * n), min_samples=config.min_periods)
    low_min3 = df["low"].rolling_min(int(3 * n), min_samples=config.min_periods)
    ts = (high_max1 + low_min1) / 2.0
    ks = (high_max2 + low_min2) / 2.0
    span_a = (ts + ks) / 2.0
    span_b = (high_max3 + low_min3) / 2.0

    s = (df["close"] - span_b) / (config.normalize_eps + span_a - span_b)
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
