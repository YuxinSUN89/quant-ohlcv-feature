import polars as pl


def signal(df, n, factor_name, config):
    # Bolling_fancy indicator (Z-score position relative to Bollinger bands)
    # Formula: result = (CLOSE - MA(CLOSE,N)) / STD(CLOSE,N)
    # Standard z-score of close price within its rolling distribution over N periods.
    # Equivalent to the Bollinger %b scaled to z-score units. Positive = above mean; negative = below.
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["close"] - df["close"].rolling_mean(n, min_samples=config.min_periods))
            / df["close"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof),
        ).fill_nan(None)
    )

    return df
