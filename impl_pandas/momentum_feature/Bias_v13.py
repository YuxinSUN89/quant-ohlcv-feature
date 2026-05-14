def signal(df, n, factor_name, config):
    # Bias_v13 indicator (Fast MA / Slow MA bias, rolling mean)
    # Formula: MAFAST = MA(CLOSE, N/2); MASLOW = MA(CLOSE, N)
    #          result = MA(MAFAST/MASLOW - 1, N)
    # Measures the smoothed ratio of a short-window MA to a long-window MA.
    # Positive values indicate short MA is consistently above long MA (uptrend); negative indicates downtrend.
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["mafast"] = df["close"].rolling(int(n / 2), min_periods=config.min_periods).mean()
    df[factor_name] = (df["mafast"] / (df["ma"] + config.eps) - 1).rolling(n, min_periods=config.min_periods).mean()

    del df["ma"], df["mafast"]

    return df
