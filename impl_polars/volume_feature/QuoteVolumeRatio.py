import polars as pl


def signal(df, n, factor_name, config):
    # QuoteVolumeRatio indicator
    # Formula: result = QUOTE_VOLUME / MA(QUOTE_VOLUME, N)
    # Measures the current quote volume relative to its rolling mean over N periods.
    # Values > 1 indicate above-average trading activity; values < 1 indicate below-average activity.
    df = df.with_columns(
        pl.Series(factor_name, df["quote_volume"] / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods))
    )

    return df
