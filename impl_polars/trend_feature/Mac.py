import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac indicator (MA Convergence: short-long MA difference, 0-1 normalized)
    # Formula: MAC = 10 * (MA(CLOSE,N) - MA(CLOSE,2N)); result = scale_01(MAC, N, config.normalize_eps)
    # Measures the difference between short and long moving averages (similar to MACD without EMA).
    # Positive values indicate short MA above long MA (uptrend); negative indicates downtrend.
    # MAC
    ma_short = df["close"].rolling_mean(n, min_samples=config.min_periods)
    ma_long = df["close"].rolling_mean(2 * n, min_samples=config.min_periods)

    _mac = 10 * (ma_short - ma_long)
    df = df.with_columns(pl.Series(factor_name, scale_01(_mac, n, config.normalize_eps, config=config)))

    return df
