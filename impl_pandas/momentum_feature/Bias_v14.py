def signal(df, n, factor_name, config):
    # Bias_v14 indicator (Volume-weighted fast/slow MA bias, rolling mean)
    # Formula: MA = MA(CLOSE,N); MAFAST = MA(CLOSE,N/2)
    #          MTM = (MAFAST/MA - 1) * (QUOTE_VOLUME / MA(QUOTE_VOLUME,N))
    #          result = MA(MTM, N)
    # Volume-weighted version of the fast/slow MA bias (Bias_v13), amplified by relative quote volume.
    # Positive rolling mean indicates sustained volume-backed uptrend.
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["ma2"] = df["close"].rolling(int(n / 2), min_periods=config.min_periods).mean()
    df["mtm"] = (
        (df["ma2"] / (df["ma"] + config.eps) - 1)
        * df["quote_volume"]
        / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)
    )
    df[factor_name] = df["mtm"].rolling(n, min_periods=config.min_periods).mean()

    del df["ma"], df["ma2"], df["mtm"]

    return df
