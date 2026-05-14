import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v3 indicator (MAC using rolling max/min midpoint)
    # Formula: PRICE = (MAX(HIGH,N) + MIN(LOW,N))/2
    #          MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps)
    # MAC computed on the rolling high-low midpoint, capturing the channel center rather than the candle midpoint.
    high = df["high"].rolling_max(n, min_samples=config.min_periods)
    low = df["low"].rolling_min(n, min_samples=config.min_periods)

    ma_short = (0.5 * high + 0.5 * low).rolling_mean(n, min_samples=config.min_periods)
    ma_long = (0.5 * high + 0.5 * low).rolling_mean(2 * n, min_samples=config.min_periods)

    _mac = 10 * (ma_short - ma_long)
    df = df.with_columns(pl.Series(factor_name, scale_01(_mac, n, config.normalize_eps, config=config)))

    return df
