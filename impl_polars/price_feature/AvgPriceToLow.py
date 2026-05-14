import polars as pl


def signal(df, n, factor_name, config):
    # AvgPriceToLow indicator (VWAP relative to current Low)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N); result = VWAP / LOW - 1
    # Measures whether the N-period VWAP is above or below the current candle's low.
    # Positive values (typical) indicate VWAP is above the low; values near 0 suggest price is near VWAP.
    df = df.with_columns(
        pl.Series(
            "price",
            df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
            / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["price"] / df["low"] - 1))

    # remove redundant columns
    df = df.drop("price")

    return df
