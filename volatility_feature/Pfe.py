def signal(df, n, factor_name, config):
    # Pfe indicator (Polar Front Efficiency — direction-signed price efficiency)
    # Formula: DIRECT_DIST = SQRT((CLOSE - REF(CLOSE, N-1))^2 + (N-1)^2)
    #          ACTUAL_DIST = SUM(SQRT(DIFF(CLOSE)^2 + 1), N-1)
    #          PFE = 100 * DIRECT_DIST / ACTUAL_DIST; PCT_CHG = (CLOSE - REF(CLOSE,N-1)) / REF(CLOSE,N-1)
    #          result = PFE * PCT_CHG
    # PFE measures how efficiently price moves from start to end of the window: 100 = perfectly straight line.
    # Multiplied by percent change, giving direction. High positive = efficient uptrend; high negative = efficient downtrend.
    # calculate the straight-line distance between the first and last prices
    totle_y = df["close"] - df["close"].shift(n - 1)
    direct_distance = (totle_y**2 + (n - 1) ** 2) ** 0.5
    # calculate the distance between adjacent prices
    each_y = df["close"].diff()
    each_distance = (each_y**2 + 1) ** 0.5
    actual_distance = each_distance.rolling(n - 1, min_periods=config.min_periods).sum()
    # calculate PFE
    PFE = 100 * (direct_distance / actual_distance)
    pct_change = (df["close"] - df["close"].shift(n - 1)) / df["close"].shift(n - 1)
    df[factor_name] = PFE * pct_change

    return df
