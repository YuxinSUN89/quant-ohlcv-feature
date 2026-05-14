def signal(df, n, factor_name, config):
    # Cse indicator (Time-series normalized close, EMA smoothed)
    # Formula: CLOSE_STD = (CLOSE - MIN(CLOSE,N)) / (MAX(CLOSE,N) - MIN(CLOSE,N))
    #          result = EMA(CLOSE_STD, N-1)
    # Normalizes close price to [0,1] within its rolling range, then smooths with EMA.
    # Values near 1 indicate close is near the top of its N-period range (bullish); near 0 indicates bottom.

    # time-series normalization
    cr = df["close"].rolling(n, min_periods=config.min_periods)
    close_standard = (df["close"] - cr.min()) / (cr.max() - cr.min())
    # exponential moving average
    df[factor_name] = close_standard.ewm(span=n - 1, min_periods=config.min_periods, adjust=config.ewm_adjust).mean()

    return df
