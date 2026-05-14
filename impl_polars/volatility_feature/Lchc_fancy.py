import polars as pl


def signal(df, n, factor_name, config):
    # Ratio of current price to the highest and lowest prices over the past N minutes, checking whether upward or downward momentum is stronger
    df = df.with_columns(
        pl.Series(
            factor_name,
            -1 * df["low"].rolling_min(n, min_samples=config.min_periods) / df["close"]
            - df["high"].rolling_max(n, min_samples=config.min_periods) / df["close"],
        )
    )

    return df
