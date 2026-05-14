def signal(df, n, factor_name, config):
    # BollingWidth indicator (Adaptive Bollinger Width)
    # Formula: Z_SCORE = |CLOSE - MA| / STD; M = MA(Z_SCORE, N) (rolling mean of z-scores)
    #          UPPER = MA + STD*M; LOWER = MA - STD*M
    #          result = 2 * STD * M / MA (= bandwidth normalized by MA)
    # An adaptive version of Bollinger bandwidth where band width is determined by the rolling
    # mean of historical z-scores rather than a fixed multiplier. Wider bands indicate higher
    # recent volatility relative to the moving average.
    eps = config.eps
    df["median"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["z_score"] = abs(df["close"] - df["median"]) / df["std"]
    df["m"] = df["z_score"].rolling(window=n, min_periods=config.min_periods).mean()
    df["upper"] = df["median"] + df["std"] * df["m"]
    df["lower"] = df["median"] - df["std"] * df["m"]
    df[factor_name] = df["std"] * df["m"] * 2 / (df["median"] + eps)

    # delete extra columns
    del df["median"], df["std"], df["z_score"], df["m"]
    del df["upper"], df["lower"]

    return df
