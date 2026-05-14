import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v5 indicator (MAC using (rolling high + rolling low + open)/3)
    # Formula: PRICE = (MAX(HIGH,N) + MIN(LOW,N) + OPEN) / 3
    #          MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps)
    # Uses a modified price that replaces close with open, alongside rolling high/low extremes.
    high = df["high"].rolling_max(n, min_samples=config.min_periods)
    low = df["low"].rolling_min(n, min_samples=config.min_periods)
    _open = df["open"]

    ma_short = ((high + low + _open) / 3.0).rolling_mean(n, min_samples=config.min_periods)
    ma_long = ((high + low + _open) / 3.0).rolling_mean(2 * n, min_samples=config.min_periods)

    _mac = 10 * (ma_short - ma_long)
    df = df.with_columns(pl.Series(factor_name, scale_01(_mac, n, config.normalize_eps, config=config)))

    return df
