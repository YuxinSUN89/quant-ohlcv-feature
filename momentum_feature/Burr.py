def signal(df, n, factor_name, config):
    # Burr indicator (pullback depth in uptrends / rebound height in downtrends)
    # Formula (uptrend): SCORE_HIGH = 1 - CLOSE / MAX(HIGH,N)  where CLOSE > OPEN shifted by N
    #          (downtrend): SCORE_LOW = 1 - CLOSE / MIN(LOW,N)  where CLOSE < OPEN shifted by N
    #          result = SCORE_HIGH + SCORE_LOW (one will always be 0)
    # In uptrends, measures how far close has pulled back from the N-period high (deeper pullback → larger value).
    # In downtrends, measures the rebound height from the N-period low. Range: [-1, 1].
    # only observe pullback magnitude during uptrends
    df["scores_high"] = (1 - df["close"] / df["high"].rolling(window=n, min_periods=config.min_periods).max()).where(
        df["close"] - df["open"].shift(n) > 0
    )
    # only observe rebound magnitude during downtrends
    df["scores_low"] = (1 - df["close"] / df["low"].rolling(window=n, min_periods=config.min_periods).min()).where(
        df["close"] - df["open"].shift(n) < 0
    )
    df[factor_name] = df["scores_high"].fillna(0) + df["scores_low"].fillna(0)  # [-1, 1]

    return df
