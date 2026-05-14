def signal(df, n, factor_name, config):
    # Bolling_fancy indicator (Z-score position relative to Bollinger bands)
    # Formula: result = (CLOSE - MA(CLOSE,N)) / STD(CLOSE,N)
    # Standard z-score of close price within its rolling distribution over N periods.
    # Equivalent to the Bollinger %b scaled to z-score units. Positive = above mean; negative = below.
    df[factor_name] = (df["close"] - df["close"].rolling(n, min_periods=config.min_periods).mean()) / df[
        "close"
    ].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)

    return df
