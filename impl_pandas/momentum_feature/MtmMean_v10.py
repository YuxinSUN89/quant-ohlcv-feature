def signal(df, n, factor_name, config):
    # MtmMean_v10 indicator (MTM mean × combined volatility)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; VOLATILITY = MAX(HIGH,N)/MIN(LOW,N)-1 (N-period range)
    #          HOURLY_VOL = HIGH/LOW-1; result = MA(MTM,N) * (VOLATILITY + MA(HOURLY_VOL,N))
    # Amplifies the momentum mean by a combined volatility measure (long-range + average intrabar).
    # High values indicate strong directional momentum in a high-volatility environment.
    df["mtm"] = df["close"] / (df["close"].shift(n) + config.eps) - 1
    df["volatility"] = (
        df["high"].rolling(n, min_periods=config.min_periods).max()
        / df["low"].rolling(n, min_periods=config.min_periods).min()
        - 1
    )
    df["hourly_volatility"] = df["high"] / df["low"] - 1
    df["hourly_volatility_mean"] = df["hourly_volatility"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean() * (
        df["volatility"] + df["hourly_volatility_mean"]
    )

    del df["mtm"], df["volatility"], df["hourly_volatility"], df["hourly_volatility_mean"]

    return df
