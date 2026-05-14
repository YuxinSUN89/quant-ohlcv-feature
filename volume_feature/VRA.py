def signal(df, n, factor_name, config):
    # VRA indicator (Volatility-adjusted Rate of change composite)
    # Formula: RC = 100 * ((HIGH - REF(HIGH,N)) / REF(CLOSE,N) + (CLOSE - REF(CLOSE,2N)) / REF(LOW,2N))
    #          RC_MEAN = MA(RC, N); VOLATILITY = STD(CLOSE,N) / MA(CLOSE,N) * 100
    #          VRA = RC_MEAN * VOLATILITY
    # Combines a dual-window price rate-of-change (using high and close) with rolling price volatility.
    # Higher values suggest strong trending momentum accompanied by elevated volatility.
    df["n_day_avg_price"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["n_day_std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["n_day_volatility"] = df["n_day_std"] / df["n_day_avg_price"] * 100
    # calculate upper and lower bands
    df["RC"] = 100 * (
        (df["high"] - df["high"].shift(n)) / df["close"].shift(n)
        + (df["close"] - df["close"].shift(2 * n)) / df["low"].shift(2 * n)
    )
    df["RC_mean"] = df["RC"].rolling(n, min_periods=config.min_periods).mean()

    # combined indicator
    df[factor_name] = df["RC_mean"] * df["n_day_volatility"]

    del df["n_day_avg_price"], df["n_day_std"], df["RC"]

    return df
