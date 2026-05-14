def signal(df, n, factor_name, config):
    # AvgPriceToLow indicator (VWAP relative to current Low)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N); result = VWAP / LOW - 1
    # Measures whether the N-period VWAP is above or below the current candle's low.
    # Positive values (typical) indicate VWAP is above the low; values near 0 suggest price is near VWAP.
    df["price"] = (
        df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
        / (df["volume"].rolling(n, min_periods=config.min_periods).sum() + config.eps)
    )
    df[factor_name] = df["price"] / df["low"] - 1

    # remove redundant columns
    del df["price"]

    return df
