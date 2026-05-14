def signal(df, n, factor_name, config):
    # AvgPrice indicator (VWAP normalized within rolling range)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N)
    #          result = (VWAP - MIN(VWAP,N)) / (MAX(VWAP,N) - MIN(VWAP,N) + eps)
    # Computes a rolling VWAP (volume-weighted average price) and normalizes it to [0,1]
    # within its N-period range. Values near 1 indicate VWAP is near its recent high; near 0 near its low.
    eps = config.eps
    df["price"] = (
        df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
        / df["volume"].rolling(n, min_periods=config.min_periods).sum()
    )
    df[factor_name] = (df["price"] - df["price"].rolling(n, min_periods=config.min_periods).min()) / (
        df["price"].rolling(n, min_periods=config.min_periods).max()
        - df["price"].rolling(n, min_periods=config.min_periods).min()
        + eps
    )

    # remove redundant columns
    del df["price"]

    return df
