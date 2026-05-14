import polars as pl


def signal(df, n, factor_name, config):
    # AvgPriceToHigh indicator (VWAP relative to current High)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N); result = VWAP / HIGH - 1
    # Measures whether the N-period VWAP is above or below the current candle's high.
    # Negative values (typical) indicate VWAP is below the high; values near 0 suggest price is near VWAP.
    df = df.with_columns(
        pl.Series(
            "price",
            df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
            / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["price"] / df["high"] - 1))

    # remove redundant columns
    df = df.drop("price")

    return df
