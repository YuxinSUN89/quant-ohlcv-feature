def signal(df, n, factor_name, config):
    # AvgPriceToHigh indicator (VWAP relative to current High)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N); result = VWAP / HIGH - 1
    # Measures whether the N-period VWAP is above or below the current candle's high.
    # Negative values (typical) indicate VWAP is below the high; values near 0 suggest price is near VWAP.
    df["price"] = (
        df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
        / (df["volume"].rolling(n, min_periods=config.min_periods).sum() + config.eps)
    )
    df[factor_name] = df["price"] / df["high"] - 1

    # remove redundant columns
    del df["price"]

    return df
