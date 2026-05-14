def signal(df, n, factor_name, config):
    # Trv indicator (Rolling percentage change of Moving Average)
    # Formula: MA = MA(CLOSE,N); TRV = 100 * (MA - REF(MA,N)) / REF(MA,N)
    #          result = MA(TRV, N)
    # Measures the smoothed N-period rate of change of the moving average.
    # Captures the velocity of the trend rather than the raw price movement.
    # calculate volatility factor
    df["ma"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["trv"] = 100 * ((df["ma"] - df["ma"].shift(n)) / (df["ma"] + config.eps).shift(n))
    df[factor_name] = df["trv"].rolling(n, min_periods=config.min_periods).mean()

    drop_col = ["ma", "trv"]
    df = df.drop(columns=drop_col)

    return df
