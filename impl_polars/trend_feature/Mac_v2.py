import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v2 indicator (MAC using (H+L)/2 price)
    # Formula: PRICE = (HIGH+LOW)/2; MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps)
    # MA convergence computed on the midpoint price instead of close.
    # More representative of the full candle range than close-only MAC.
    ma_short = (0.5 * df["high"] + 0.5 * df["low"]).rolling_mean(n, min_samples=config.min_periods)
    ma_long = (0.5 * df["high"] + 0.5 * df["low"]).rolling_mean(2 * n, min_samples=config.min_periods)

    _mac = 10 * (ma_short - ma_long)
    df = df.with_columns(pl.Series(factor_name, scale_01(_mac, n, config.normalize_eps, config=config)))

    return df
