import polars as pl


def signal(df, n, factor_name, config):
    # Volume indicator (Rolling sum of quote volume)
    # Formula: result = SUM(QUOTE_VOLUME, N)
    # Sums quote volume over N periods, representing the total traded dollar value in the window.
    # A simple measure of market participation and liquidity over recent candles.
    df = df.with_columns(pl.Series(factor_name, df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)))

    return df
