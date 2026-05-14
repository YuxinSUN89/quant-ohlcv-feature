import polars as pl


def signal(df, n, factor_name, config):
    # Bias36ma indicator (Rolling MA of MA3-MA6 bias)
    # Formula: BIAS36 = MA(CLOSE, 3) - MA(CLOSE, 6); result = MA(BIAS36, N)
    # Measures the smoothed difference between short (3-period) and medium (6-period) moving averages.
    # Positive values indicate short MA is above long MA (uptrend); negative indicates downtrend.
    bias36 = df["close"].rolling_mean(3, min_samples=config.min_periods) - df["close"].rolling_mean(
        6, min_samples=config.min_periods
    )
    df = df.with_columns(pl.Series(factor_name, bias36.rolling_mean(n, min_samples=config.min_periods)))

    return df
